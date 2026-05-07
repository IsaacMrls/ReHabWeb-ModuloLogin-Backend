"""Serializers for authentication flows in RehabWeb_API."""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from RehabWeb_API.models import TherapistProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	role = serializers.SerializerMethodField()
	specialty = serializers.SerializerMethodField()
	professional_license = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = (
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'role',
			'specialty',
			'professional_license',
		)

	def get_role(self, obj):
		return 'therapist' if hasattr(obj, 'therapist_profile') else 'patient'

	def get_specialty(self, obj):
		profile = getattr(obj, 'therapist_profile', None)
		return profile.specialty if profile else None

	def get_professional_license(self, obj):
		profile = getattr(obj, 'therapist_profile', None)
		return profile.professional_license if profile else None


class RegisterSerializer(serializers.ModelSerializer):
	ROLE_CHOICES = ('patient', 'therapist')

	role = serializers.ChoiceField(choices=ROLE_CHOICES, write_only=True)
	password = serializers.CharField(write_only=True, min_length=8)
	password_confirm = serializers.CharField(write_only=True)
	specialty = serializers.CharField(write_only=True, required=False, allow_blank=True)
	professional_license = serializers.CharField(
		write_only=True,
		required=False,
		allow_blank=True,
	)

	class Meta:
		model = User
		fields = (
			'role',
			'username',
			'email',
			'first_name',
			'last_name',
			'specialty',
			'professional_license',
			'password',
			'password_confirm',
		)

	def validate(self, attrs):
		if attrs['password'] != attrs['password_confirm']:
			raise serializers.ValidationError(
				{'password_confirm': 'Las contraseñas no coinciden.'}
			)

		if attrs['role'] == 'therapist':
			if not attrs.get('specialty', '').strip():
				raise serializers.ValidationError(
					{'specialty': 'La especialidad es obligatoria para terapeutas.'}
				)
			if not attrs.get('professional_license', '').strip():
				raise serializers.ValidationError(
					{'professional_license': 'La cédula profesional es obligatoria para terapeutas.'}
				)
		return attrs

	def validate_email(self, value):
		if User.objects.filter(email__iexact=value).exists():
			raise serializers.ValidationError('Este correo ya está registrado.')
		return value

	def validate_professional_license(self, value):
		if not value:
			return value

		normalized = value.strip().upper()
		if TherapistProfile.objects.filter(
			professional_license__iexact=normalized
		).exists():
			raise serializers.ValidationError('Esta cédula profesional ya está registrada.')
		return normalized

	def create(self, validated_data):
		role = validated_data.pop('role')
		specialty = validated_data.pop('specialty', '').strip()
		professional_license = validated_data.pop('professional_license', '').strip().upper()
		validated_data.pop('password_confirm')
		password = validated_data.pop('password')

		user = User(**validated_data)
		user.set_password(password)
		user.save()

		if role == 'therapist':
			TherapistProfile.objects.create(
				user=user,
				specialty=specialty,
				professional_license=professional_license,
			)

		return user


class LoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField(write_only=True)

	def validate(self, attrs):
		user = authenticate(
			username=attrs.get('username'),
			password=attrs.get('password'),
		)

		if not user:
			raise serializers.ValidationError(
				{'non_field_errors': ['Credenciales inválidas.']}
			)

		attrs['user'] = user
		return attrs
