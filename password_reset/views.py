from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

import json
import random

# Guardado temporal
verification_codes = {}


@csrf_exempt
def send_code(request):

	if request.method == 'POST':

		data = json.loads(request.body)
		email = data.get('email')

		try:
			User.objects.get(email=email)

			code = str(random.randint(100000, 999999))

			# Guardar código
			verification_codes[email] = code

			send_mail(
				'Código de recuperación',
				f'Tu código de recuperación es: {code}',
				settings.EMAIL_HOST_USER,
				[email],
				fail_silently=False,
			)

			return JsonResponse({
				'success': True,
				'message': 'Código enviado'
			})

		except User.DoesNotExist:

			return JsonResponse({
				'success': False,
				'message': 'Correo no encontrado'
			})

	return JsonResponse({
		'success': False,
		'message': 'Método no permitido'
	})


@csrf_exempt
def verify_code(request):

	if request.method == 'POST':

		data = json.loads(request.body)

		email = data.get('email')
		code = data.get('code')

		saved_code = verification_codes.get(email)

		if saved_code == code:

			return JsonResponse({
				'success': True,
				'message': 'Código correcto'
			})

		return JsonResponse({
			'success': False,
			'message': 'Código incorrecto'
		})

	return JsonResponse({
		'success': False,
		'message': 'Método no permitido'
	})


@csrf_exempt
def reset_password(request):

	if request.method == 'POST':

		data = json.loads(request.body)

		email = data.get('email')
		new_password = data.get('new_password')

		if not new_password or len(new_password) < 8:
			return JsonResponse({
				'success': False,
				'message': 'La contraseña debe tener al menos 8 caracteres'
			})

		try:
			user = User.objects.get(email=email)

			user.set_password(new_password)
			user.save()

			return JsonResponse({
				'success': True,
				'message': 'Contraseña actualizada correctamente'
			})

		except User.DoesNotExist:

			return JsonResponse({
				'success': False,
				'message': 'Usuario no encontrado'
			})

	return JsonResponse({
		'success': False,
		'message': 'Método no permitido'
	})
