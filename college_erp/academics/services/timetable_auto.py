from collections import defaultdict
from datetime import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from django.db import transaction
from django.db.models import Q

from academics.models import Subject, SubjectFacultyMapping, TimeSlot, Timetable, TimetableMapping


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
PERIODS = [1, 2, 3, 4, 5, 6, 7]
TIME_LABELS = {
    1: ("09:30", "10:20"),
    2: ("10:20", "11:10"),
    3: ("11:30", "12:20"),
    4: ("12:20", "13:10"),
    5: ("14:00", "14:50"),
    6: ("14:50", "15:40"),
    7: ("15:40", "16:30"),
}

THEORY_REQUIRED_COUNT = 6
PRACTICAL_REQUIRED_COUNT = 3
THEORY_PERIODS_PER_SUBJECT = 5
PRACTICAL_PERIODS_PER_SUBJECT = 3
CRT_PERIODS_PER_WEEK = 2
MENTORING_PERIODS_PER_WEEK = 1

VALID_PRACTICAL_BLOCKS: Tuple[Tuple[int, int, int], ...] = ((1, 2, 3), (2, 3, 4), (5, 6, 7))
MORNING_BLOCKS = {(1, 2, 3), (2, 3, 4)}
AFTERNOON_BLOCKS = {(5, 6, 7)}

MAX_DAILY_FACULTY_WORKLOAD = 6
MAX_WEEKLY_FACULTY_WORKLOAD = 30


class TimetableGenerationError(Exception):
    pass


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":")
    return time(hour=int(hh), minute=int(mm))


def _ensure_time_slots() -> Dict[Tuple[str, int], TimeSlot]:
    slots: Dict[Tuple[str, int], TimeSlot] = {}
    for day in DAYS:
        for period in PERIODS:
            start_s, end_s = TIME_LABELS[period]
            slot, _ = TimeSlot.objects.get_or_create(
                day=day,
                period_number=period,
                defaults={"start_time": _parse_hhmm(start_s), "end_time": _parse_hhmm(end_s)},
            )
            slots[(day, period)] = slot
    return slots


def get_all_slots() -> List[Tuple[str, int]]:
    return [(day, period) for day in DAYS for period in PERIODS]


def is_valid_practical_block(block: Sequence[int]) -> bool:
    return tuple(block) in VALID_PRACTICAL_BLOCKS


def _subject_pool(academic_year: str, branch: str, semester: str, regulation: str):
    subjects = list(
        Subject.objects.filter(
            academic_year=academic_year,
            branch=branch,
            semester=semester,
            regulation=regulation,
        ).order_by("subject_id")
    )
    theory = [s for s in subjects if s.subject_type == "THEORY"]
    practical = [s for s in subjects if s.subject_type == "PRACTICAL"]
    crt = [s for s in subjects if s.subject_type == "CRT"]
    mentoring = [s for s in subjects if s.subject_type == "MENTORING"]
    return theory, practical, crt, mentoring


def _subject_faculty_for_class(
    *,
    academic_year: str,
    branch: str,
    semester: str,
    section: str,
    regulation: str,
) -> Dict[str, int]:
    rows = SubjectFacultyMapping.objects.filter(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    ).select_related("subject")

    by_subject: Dict[str, set] = defaultdict(set)
    for row in rows:
        by_subject[row.subject.subject_id].add(row.faculty_id)

    result: Dict[str, int] = {}
    for subject_id, faculty_ids in by_subject.items():
        if len(faculty_ids) > 1:
            raise TimetableGenerationError(
                f"Subject {subject_id} is mapped to multiple faculties. Keep one faculty per subject."
            )
        result[subject_id] = next(iter(faculty_ids))
    return result


def _build_external_faculty_occupancy(
    *,
    academic_year: str,
    branch: str,
    semester: str,
    section: str,
    regulation: str,
):
    busy = defaultdict(set)
    day_load = defaultdict(int)
    week_load = defaultdict(int)

    def _mark(fid: int, day: str, period: int):
        key = (day, period)
        if key in busy[fid]:
            return
        busy[fid].add(key)
        day_load[(fid, day)] += 1
        week_load[fid] += 1

    manual_rows = TimetableMapping.objects.exclude(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
    ).values("faculty_id", "week_day", "period_no")
    for row in manual_rows:
        _mark(row["faculty_id"], row["week_day"], row["period_no"])

    subject_faculty_rows = SubjectFacultyMapping.objects.values(
        "academic_year",
        "branch",
        "semester",
        "section",
        "regulation",
        "subject__subject_id",
        "faculty_id",
    )
    subject_faculty = defaultdict(set)
    for row in subject_faculty_rows:
        key = (
            row["academic_year"],
            row["branch"],
            row["semester"],
            row["section"],
            row["regulation"],
            row["subject__subject_id"],
        )
        subject_faculty[key].add(row["faculty_id"])

    auto_rows = Timetable.objects.exclude(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    ).values(
        "academic_year",
        "branch",
        "semester",
        "section",
        "regulation",
        "day",
        "period_no",
        "subject__subject_id",
    )
    for row in auto_rows:
        key = (
            row["academic_year"],
            row["branch"],
            row["semester"],
            row["section"],
            row["regulation"],
            row["subject__subject_id"],
        )
        for fid in subject_faculty.get(key, set()):
            _mark(fid, row["day"], row["period_no"])

    return busy, day_load, week_load


def _copy_faculty_state(busy, day_load, week_load):
    next_busy = defaultdict(set)
    for fid, slots in busy.items():
        next_busy[fid] = set(slots)
    next_day_load = defaultdict(int)
    next_day_load.update(day_load)
    next_week_load = defaultdict(int)
    next_week_load.update(week_load)
    return next_busy, next_day_load, next_week_load


def check_faculty_conflict(
    *,
    faculty_id: int,
    day: str,
    period: int,
    busy,
    day_load,
    week_load,
) -> bool:
    if (day, period) in busy[faculty_id]:
        return True
    if day_load[(faculty_id, day)] >= MAX_DAILY_FACULTY_WORKLOAD:
        return True
    if week_load[faculty_id] >= MAX_WEEKLY_FACULTY_WORKLOAD:
        return True
    return False


def _assign_faculty(faculty_id: int, day: str, period: int, busy, day_load, week_load):
    busy[faculty_id].add((day, period))
    day_load[(faculty_id, day)] += 1
    week_load[faculty_id] += 1


def _unassign_faculty(faculty_id: int, day: str, period: int, busy, day_load, week_load):
    busy[faculty_id].discard((day, period))
    day_load[(faculty_id, day)] = max(0, day_load[(faculty_id, day)] - 1)
    week_load[faculty_id] = max(0, week_load[faculty_id] - 1)


def _initialize_board() -> Dict[str, Dict[int, Optional[str]]]:
    return {day: {period: None for period in PERIODS} for day in DAYS}


def _practical_slot_conflict_exists(
    *,
    day: str,
    period_no: int,
    academic_year: str,
    branch: str,
    semester: str,
    section: str,
    regulation: str,
) -> bool:
    current_class_q = Q(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    )
    auto_conflict = (
        Timetable.objects.filter(day=day, period_no=period_no, branch=branch, subject__subject_type="PRACTICAL")
        .exclude(current_class_q)
        .exists()
    )
    manual_conflict = (
        TimetableMapping.objects.filter(week_day=day, period_no=period_no, branch=branch, subject__subject_type="PRACTICAL")
        .exclude(academic_year=academic_year, semester=semester, section=section)
        .exists()
    )
    return auto_conflict or manual_conflict


def place_practicals(
    *,
    board,
    practical_subjects,
    subject_faculty_map,
    busy,
    day_load,
    week_load,
    academic_year: str,
    branch: str,
    semester: str,
    section: str,
    regulation: str,
    attempt: int,
) -> bool:
    day_order = DAYS[attempt % len(DAYS) :] + DAYS[: attempt % len(DAYS)]
    block_order = list(VALID_PRACTICAL_BLOCKS)
    if attempt % 2 == 1:
        block_order = [VALID_PRACTICAL_BLOCKS[2], VALID_PRACTICAL_BLOCKS[1], VALID_PRACTICAL_BLOCKS[0]]

    subject_ids = [s.subject_id for s in practical_subjects]
    candidates_by_subject: Dict[str, List[Tuple[str, Tuple[int, int, int]]]] = {}
    for sid in subject_ids:
        fid = subject_faculty_map[sid]
        options: List[Tuple[str, Tuple[int, int, int]]] = []
        for day in day_order:
            for block in block_order:
                if not is_valid_practical_block(block):
                    continue
                if any(_practical_slot_conflict_exists(
                    day=day,
                    period_no=period,
                    academic_year=academic_year,
                    branch=branch,
                    semester=semester,
                    section=section,
                    regulation=regulation,
                ) for period in block):
                    continue
                if any(board[day][period] is not None for period in block):
                    continue
                if any(
                    check_faculty_conflict(
                        faculty_id=fid,
                        day=day,
                        period=period,
                        busy=busy,
                        day_load=day_load,
                        week_load=week_load,
                    )
                    for period in block
                ):
                    continue
                options.append((day, block))
        candidates_by_subject[sid] = options

    subject_ids.sort(key=lambda sid: len(candidates_by_subject[sid]))
    used_days = set()
    morning_blocks = 0
    afternoon_blocks = 0

    def _dfs(index: int) -> bool:
        nonlocal morning_blocks, afternoon_blocks
        if index == len(subject_ids):
            return morning_blocks > 0 and afternoon_blocks > 0

        sid = subject_ids[index]
        fid = subject_faculty_map[sid]
        for day, block in candidates_by_subject[sid]:
            if day in used_days:
                continue
            if any(board[day][p] is not None for p in block):
                continue
            if any(
                check_faculty_conflict(
                    faculty_id=fid,
                    day=day,
                    period=period,
                    busy=busy,
                    day_load=day_load,
                    week_load=week_load,
                )
                for period in block
            ):
                continue

            used_days.add(day)
            for period in block:
                board[day][period] = sid
                _assign_faculty(fid, day, period, busy, day_load, week_load)

            is_morning = block in MORNING_BLOCKS
            if is_morning:
                morning_blocks += 1
            else:
                afternoon_blocks += 1

            if _dfs(index + 1):
                return True

            if is_morning:
                morning_blocks -= 1
            else:
                afternoon_blocks -= 1
            for period in block:
                board[day][period] = None
                _unassign_faculty(fid, day, period, busy, day_load, week_load)
            used_days.remove(day)
        return False

    return _dfs(0)


def place_mentoring(*, board, mentoring_subject, subject_faculty_map, busy, day_load, week_load) -> bool:
    sid = mentoring_subject.subject_id
    fid = subject_faculty_map[sid]

    preferred = [("Saturday", 7)]
    preferred += [("Saturday", period) for period in reversed(PERIODS) if period != 7]
    fallback = [(day, period) for day in DAYS for period in reversed(PERIODS) if (day, period) not in preferred]

    for day, period in preferred + fallback:
        if board[day][period] is not None:
            continue
        if check_faculty_conflict(
            faculty_id=fid,
            day=day,
            period=period,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            continue
        board[day][period] = sid
        _assign_faculty(fid, day, period, busy, day_load, week_load)
        return True
    return False


def place_crt(*, board, crt_subject, subject_faculty_map, busy, day_load, week_load) -> bool:
    sid = crt_subject.subject_id
    fid = subject_faculty_map[sid]
    placed: List[Tuple[str, int]] = []

    preferred = [
        ("Tuesday", 1),
        ("Thursday", 1),
        ("Wednesday", 2),
        ("Friday", 2),
        ("Saturday", 2),
        ("Monday", 2),
    ]
    fallback = [(day, period) for day in DAYS for period in PERIODS if (day, period) not in preferred]

    for day, period in preferred + fallback:
        if len(placed) >= CRT_PERIODS_PER_WEEK:
            break
        if day == "Monday" and period == 1:
            continue
        if board[day][period] is not None:
            continue
        if any(p_day == day and abs(p_period - period) == 1 for p_day, p_period in placed):
            continue
        if check_faculty_conflict(
            faculty_id=fid,
            day=day,
            period=period,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            continue
        board[day][period] = sid
        _assign_faculty(fid, day, period, busy, day_load, week_load)
        placed.append((day, period))
    return len(placed) == CRT_PERIODS_PER_WEEK


def _slot_candidates(
    *,
    day: str,
    period: int,
    board,
    remaining,
    day_subject_count,
    subject_day_presence,
    subject_faculty_map,
    busy,
    day_load,
    week_load,
) -> List[str]:
    prev_sid = board[day].get(period - 1)
    next_sid = board[day].get(period + 1)
    candidates = []
    for sid, left in remaining.items():
        if left <= 0:
            continue
        if day_subject_count[day][sid] >= 2:
            continue
        if prev_sid == sid or next_sid == sid:
            continue
        fid = subject_faculty_map[sid]
        if check_faculty_conflict(
            faculty_id=fid,
            day=day,
            period=period,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            continue
        candidates.append(sid)

    candidates.sort(
        key=lambda sid: (
            day_subject_count[day][sid],
            len(subject_day_presence[sid]),
            -remaining[sid],
            sid,
        )
    )
    return candidates


def place_theory(*, board, theory_subjects, subject_faculty_map, busy, day_load, week_load) -> bool:
    remaining = {subject.subject_id: THEORY_PERIODS_PER_SUBJECT for subject in theory_subjects}
    day_subject_count = defaultdict(lambda: defaultdict(int))
    subject_day_presence = defaultdict(set)

    for day in DAYS:
        for period in PERIODS:
            sid = board[day][period]
            if sid is None:
                continue
            day_subject_count[day][sid] += 1
            subject_day_presence[sid].add(day)

    def _open_slots():
        return [(d, p) for d, p in get_all_slots() if board[d][p] is None]

    if len(_open_slots()) != THEORY_REQUIRED_COUNT * THEORY_PERIODS_PER_SUBJECT:
        raise TimetableGenerationError("Weekly slot distribution does not match required 30 theory periods.")

    def _pick_next_slot():
        open_slots = _open_slots()
        best = None
        best_candidates = None
        for day, period in open_slots:
            cands = _slot_candidates(
                day=day,
                period=period,
                board=board,
                remaining=remaining,
                day_subject_count=day_subject_count,
                subject_day_presence=subject_day_presence,
                subject_faculty_map=subject_faculty_map,
                busy=busy,
                day_load=day_load,
                week_load=week_load,
            )
            if best is None or len(cands) < len(best_candidates):
                best = (day, period)
                best_candidates = cands
                if len(best_candidates) <= 1:
                    break
        return best, best_candidates or []

    def _dfs() -> bool:
        if all(v == 0 for v in remaining.values()):
            return all(board[d][p] is not None for d, p in get_all_slots())

        slot, candidates = _pick_next_slot()
        if slot is None or not candidates:
            return False
        day, period = slot

        for sid in candidates:
            fid = subject_faculty_map[sid]
            board[day][period] = sid
            remaining[sid] -= 1
            day_subject_count[day][sid] += 1
            subject_day_presence[sid].add(day)
            _assign_faculty(fid, day, period, busy, day_load, week_load)

            if _dfs():
                return True

            _unassign_faculty(fid, day, period, busy, day_load, week_load)
            day_subject_count[day][sid] -= 1
            if day_subject_count[day][sid] == 0:
                subject_day_presence[sid].discard(day)
            remaining[sid] += 1
            board[day][period] = None
        return False

    return _dfs()


def _count_subject_slots(board) -> Dict[str, List[Tuple[str, int]]]:
    subject_slots = defaultdict(list)
    for day in DAYS:
        for period in PERIODS:
            sid = board[day][period]
            if sid is not None:
                subject_slots[sid].append((day, period))
    return subject_slots


def validate_full_schedule(
    *,
    board,
    theory_subjects,
    practical_subjects,
    crt_subject,
    mentoring_subject,
    subject_faculty_map,
    external_busy,
    external_day_load,
    external_week_load,
) -> None:
    all_slots = get_all_slots()
    if any(board[day][period] is None for day, period in all_slots):
        raise TimetableGenerationError("No empty periods allowed.")
    if sum(1 for day, period in all_slots if board[day][period] is not None) != 42:
        raise TimetableGenerationError("Total weekly periods must be exactly 42.")

    subject_slots = _count_subject_slots(board)

    for subject in theory_subjects:
        if len(subject_slots.get(subject.subject_id, [])) != THEORY_PERIODS_PER_SUBJECT:
            raise TimetableGenerationError(f"Theory subject {subject.subject_id} must have exactly 5 periods.")
    for subject in practical_subjects:
        slots = subject_slots.get(subject.subject_id, [])
        if len(slots) != PRACTICAL_PERIODS_PER_SUBJECT:
            raise TimetableGenerationError(f"Practical subject {subject.subject_id} must have exactly 3 periods.")
        grouped = defaultdict(list)
        for day, period in slots:
            grouped[day].append(period)
        if len(grouped) != 1:
            raise TimetableGenerationError(f"Practical subject {subject.subject_id} must be in the same day.")
        day_periods = sorted(next(iter(grouped.values())))
        if not is_valid_practical_block(day_periods):
            raise TimetableGenerationError(
                f"Practical subject {subject.subject_id} must be one of: (1,2,3), (2,3,4), (5,6,7)."
            )

    practical_morning = 0
    practical_afternoon = 0
    for subject in practical_subjects:
        slots = subject_slots[subject.subject_id]
        periods = tuple(sorted(period for _, period in slots))
        if periods in MORNING_BLOCKS:
            practical_morning += 1
        if periods in AFTERNOON_BLOCKS:
            practical_afternoon += 1
    if practical_morning == 0 or practical_afternoon == 0:
        raise TimetableGenerationError("Practical distribution must include both morning and afternoon blocks.")

    if len(subject_slots.get(crt_subject.subject_id, [])) != CRT_PERIODS_PER_WEEK:
        raise TimetableGenerationError("CRT must have exactly 2 periods.")
    if board["Monday"][1] == crt_subject.subject_id:
        raise TimetableGenerationError("CRT cannot be scheduled in Monday 1st period.")

    if len(subject_slots.get(mentoring_subject.subject_id, [])) != MENTORING_PERIODS_PER_WEEK:
        raise TimetableGenerationError("Mentoring must have exactly 1 period.")

    for day in DAYS:
        day_counts = defaultdict(int)
        for period in PERIODS:
            sid = board[day][period]
            day_counts[sid] += 1
        for subject in theory_subjects + [crt_subject, mentoring_subject]:
            if day_counts[subject.subject_id] > 2:
                raise TimetableGenerationError(f"Subject {subject.subject_id} cannot appear more than 2 times in a day.")

    busy, day_load, week_load = _copy_faculty_state(external_busy, external_day_load, external_week_load)
    for day, period in all_slots:
        sid = board[day][period]
        fid = subject_faculty_map[sid]
        if check_faculty_conflict(
            faculty_id=fid,
            day=day,
            period=period,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            raise TimetableGenerationError(
                f"Faculty clash detected for subject {sid} on {day} period {period}."
            )
        _assign_faculty(fid, day, period, busy, day_load, week_load)


def _serialize(board, subject_name_map):
    data = {}
    for day in DAYS:
        data[day] = []
        for period in PERIODS:
            start_s, end_s = TIME_LABELS[period]
            sid = board[day][period]
            data[day].append(
                {
                    "period": period,
                    "time": f"{start_s}-{end_s}",
                    "subject": subject_name_map.get(sid, sid),
                    "subject_code": sid,
                }
            )
    return data


@transaction.atomic
def auto_generate_timetable(
    *,
    class_id: str,
    academic_year: str,
    branch: str,
    semester: str,
    section: str,
    regulation: str,
):
    theory_pool, practical_pool, crt_pool, mentoring_pool = _subject_pool(academic_year, branch, semester, regulation)

    if len(theory_pool) < THEORY_REQUIRED_COUNT:
        raise TimetableGenerationError("At least 6 THEORY subjects are required.")
    if len(practical_pool) < PRACTICAL_REQUIRED_COUNT:
        raise TimetableGenerationError("At least 3 PRACTICAL subjects are required.")
    if not crt_pool:
        raise TimetableGenerationError("At least 1 CRT subject is required.")
    if not mentoring_pool:
        raise TimetableGenerationError("At least 1 MENTORING subject is required.")

    theory_subjects = theory_pool[:THEORY_REQUIRED_COUNT]
    practical_subjects = practical_pool[:PRACTICAL_REQUIRED_COUNT]
    crt_subject = crt_pool[0]
    mentoring_subject = mentoring_pool[0]
    selected_subjects = theory_subjects + practical_subjects + [crt_subject, mentoring_subject]

    subject_faculty_map = _subject_faculty_for_class(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    )
    for subject in selected_subjects:
        if subject.subject_id not in subject_faculty_map:
            raise TimetableGenerationError(
                f"No faculty mapping found for subject {subject.subject_id}. Save subject-faculty mapping first."
            )

    external_busy, external_day_load, external_week_load = _build_external_faculty_occupancy(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    )

    board = None
    last_error = None
    for attempt in range(10):
        board = _initialize_board()
        busy, day_load, week_load = _copy_faculty_state(external_busy, external_day_load, external_week_load)

        ok_practical = place_practicals(
            board=board,
            practical_subjects=practical_subjects,
            subject_faculty_map=subject_faculty_map,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
            academic_year=academic_year,
            branch=branch,
            semester=semester,
            section=section,
            regulation=regulation,
            attempt=attempt,
        )
        if not ok_practical:
            last_error = "Unable to place practical blocks with updated constraints."
            continue

        if not place_mentoring(
            board=board,
            mentoring_subject=mentoring_subject,
            subject_faculty_map=subject_faculty_map,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            last_error = "Unable to place Mentoring period without faculty clash."
            continue

        if not place_crt(
            board=board,
            crt_subject=crt_subject,
            subject_faculty_map=subject_faculty_map,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            last_error = "Unable to place CRT periods without faculty clash."
            continue

        if not place_theory(
            board=board,
            theory_subjects=theory_subjects,
            subject_faculty_map=subject_faculty_map,
            busy=busy,
            day_load=day_load,
            week_load=week_load,
        ):
            last_error = "Unable to place theory subjects with current constraints."
            continue

        try:
            validate_full_schedule(
                board=board,
                theory_subjects=theory_subjects,
                practical_subjects=practical_subjects,
                crt_subject=crt_subject,
                mentoring_subject=mentoring_subject,
                subject_faculty_map=subject_faculty_map,
                external_busy=external_busy,
                external_day_load=external_day_load,
                external_week_load=external_week_load,
            )
            break
        except TimetableGenerationError as exc:
            last_error = str(exc)
            board = None
            continue

    if board is None:
        raise TimetableGenerationError(last_error or "Unable to generate timetable.")

    subject_map = {subject.subject_id: subject for subject in selected_subjects}
    subject_name_map = {subject.subject_id: subject.subject_name for subject in selected_subjects}
    slot_map = _ensure_time_slots()

    Timetable.objects.filter(
        academic_year=academic_year,
        branch=branch,
        semester=semester,
        section=section,
        regulation=regulation,
    ).delete()

    rows = []
    for day, period in get_all_slots():
        sid = board[day][period]
        rows.append(
            Timetable(
                academic_year=academic_year,
                branch=branch,
                semester=semester,
                section=section,
                regulation=regulation,
                day=day,
                period_no=period,
                subject=subject_map[sid],
                timeslot=slot_map[(day, period)],
            )
        )
    Timetable.objects.bulk_create(rows)

    data = _serialize(board, subject_name_map)
    data["_meta"] = {"class_id": class_id}
    return data
