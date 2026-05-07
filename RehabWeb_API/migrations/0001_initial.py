from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	initial = True

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='TherapistProfile',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('specialty', models.CharField(max_length=120)),
				('professional_license', models.CharField(max_length=25, unique=True)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='therapist_profile', to=settings.AUTH_USER_MODEL)),
			],
			options={
				'verbose_name': 'Perfil de terapeuta',
				'verbose_name_plural': 'Perfiles de terapeuta',
			},
		),
	]