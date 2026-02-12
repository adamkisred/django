import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from accounts.models import User, EmailOTP


# =====================================================
# STEP 1: CHECK USER & SEND OTP (STUDENT)
# =====================================================
class LoginRouterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier", "").strip().lower()

        if not identifier:
            return Response(
                {"success": False, "message": "Identifier required"},
                status=400
            )

        # -------------------------
        # STUDENT LOGIN (EMAIL)
        # -------------------------
        if "@" in identifier:
            try:
                user = User.objects.get(email=identifier, role="STUDENT")
            except User.DoesNotExist:
                return Response(
                    {"success": False, "message": "Student email not registered"},
                    status=404
                )

            # 🔐 Generate OTP
            otp = f"{random.randint(100000, 999999)}"

            EmailOTP.objects.create(
                email=identifier,
                otp=otp,
            )

            # 📧 SEND EMAIL
            send_mail(
                subject="Your Login OTP",
                message=f"Your OTP is {otp}. It is valid for 5 minutes.",
                from_email="noreply@collegeerp.com",
                recipient_list=[identifier],
                fail_silently=False,
            )

            return Response({
                "success": True,
                "next_step": "OTP_VERIFICATION",
                "identifier": identifier,
            })

        # -------------------------
        # FACULTY / ADMIN LOGIN
        # -------------------------
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Username not found"},
                status=404
            )

        return Response({
            "success": True,
            "next_step": "PASSWORD_REQUIRED",
            "identifier": identifier,
        })


# =====================================================
# STEP 2: VERIFY OTP OR PASSWORD
# =====================================================
class VerifyLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_type = request.data.get("type")

        # -------------------------
        # OTP LOGIN (STUDENT)
        # -------------------------
        if login_type == "otp":
            email = request.data.get("identifier")
            otp = request.data.get("otp")

            otp_obj = EmailOTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False,
                created_at__gte=now() - timedelta(minutes=5)
            ).first()

            if not otp_obj:
                return Response(
                    {"success": False, "message": "Invalid or expired OTP"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            otp_obj.is_used = True
            otp_obj.save()

            user = User.objects.get(email=email)

            return Response({
                "success": True,
                "role": user.role,
                "token": "dummy-token"
            })

        # -------------------------
        # PASSWORD LOGIN
        # -------------------------
        username = request.data.get("identifier")
        password = request.data.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=401
            )

        if not user.check_password(password):
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=401
            )

        return Response({
            "success": True,
            "role": user.role,
            "token": "dummy-token"
        })
