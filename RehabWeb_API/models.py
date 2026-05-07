from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TherapistProfile(models.Model):
	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		related_name='therapist_profile',
	)
	specialty = models.CharField(max_length=120)
	professional_license = models.CharField(max_length=25, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Perfil de terapeuta'
		verbose_name_plural = 'Perfiles de terapeuta'

	def __str__(self):
		return f'{self.user.username} - {self.specialty}'
