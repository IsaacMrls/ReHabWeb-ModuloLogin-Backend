"""Authentication API views for RehabWeb_API."""

import random
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from RehabWeb_API.serializers import (
	Login2FAVerifySerializer,
	LoginSerializer,
	RegisterSerializer,
	UserSerializer,
)

LOGIN_2FA_CACHE_PREFIX = 'login_2fa:'
LOGIN_2FA_TTL_SECONDS = 300


def _mask_email(email: str) -> str:
	username, _, domain = email.partition('@')
	if not domain:
		return email

	if len(username) <= 2:
		masked_user = username[0] + '*' if username else '*'
	else:
		masked_user = username[0] + ('*' * (len(username) - 2)) + username[-1]

	return f'{masked_user}@{domain}'


class RegisterView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		token, _ = Token.objects.get_or_create(user=user)

		return Response(
			{
				'token': token.key,
				'user': UserSerializer(user).data,
			},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		token, _ = Token.objects.get_or_create(user=user)

		return Response(
			{
				'token': token.key,
				'user': UserSerializer(user).data,
			},
			status=status.HTTP_200_OK,
		)


class LoginRequestCodeView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']

		if not user.email:
			return Response(
				{'detail': 'El usuario no tiene un correo registrado.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		code = f'{random.randint(100000, 999999)}'
		login_session = str(uuid4())

		cache.set(
			f'{LOGIN_2FA_CACHE_PREFIX}{login_session}',
			{'user_id': user.id, 'code': code},
			LOGIN_2FA_TTL_SECONDS,
		)

		send_mail(
			'Codigo de acceso - RehabWeb',
			f'Tu codigo de acceso es: {code}. Este codigo expira en 5 minutos.',
			settings.EMAIL_HOST_USER,
			[user.email],
			fail_silently=False,
		)

		return Response(
			{
				'requires_2fa': True,
				'login_session': login_session,
				'email_masked': _mask_email(user.email),
				'message': 'Codigo enviado al correo registrado.',
			},
			status=status.HTTP_200_OK,
		)


class LoginVerifyCodeView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = Login2FAVerifySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		login_session = serializer.validated_data['login_session']
		code = serializer.validated_data['code']

		cache_key = f'{LOGIN_2FA_CACHE_PREFIX}{login_session}'
		cached_data = cache.get(cache_key)

		if not cached_data:
			return Response(
				{'detail': 'El codigo expiro o la sesion no es valida.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if cached_data['code'] != code:
			return Response(
				{'detail': 'Codigo de acceso incorrecto.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		from django.contrib.auth import get_user_model

		User = get_user_model()
		user = User.objects.filter(id=cached_data['user_id']).first()

		if not user:
			return Response(
				{'detail': 'Usuario no encontrado para esta sesion.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		cache.delete(cache_key)
		token, _ = Token.objects.get_or_create(user=user)

		return Response(
			{
				'token': token.key,
				'user': UserSerializer(user).data,
			},
			status=status.HTTP_200_OK,
		)


class ProfileView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
