from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .models import OTPCode
from .serializers import (
    RegisterSerializer, UserSerializer,
    RequestOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RequestOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Si el email existe, recibirás un código.'})

        OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)

        code = str(random.randint(100000, 999999))
        OTPCode.objects.create(user=user, code=code)

        print(f"\n{'='*40}")
        print(f"  OTP para {user.username} ({email}): {code}")
        print(f"  Válido por 10 minutos")
        print(f"{'='*40}\n")

        return Response({'message': 'Si el email existe, recibirás un código.'})

class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = OTPCode.objects.filter(user=user, code=code, is_used=False).last()

        if not otp or not otp.is_valid():
            return Response({'error': 'Código inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Código válido. Podés cambiar tu contraseña.'})

class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = OTPCode.objects.filter(user=user, code=code, is_used=False).last()

        if not otp or not otp.is_valid():
            return Response({'error': 'Código inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save()

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Contraseña actualizada correctamente.'})