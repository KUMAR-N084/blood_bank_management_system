from django.db import migrations


def create_demo_user(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = 'demo_staff'
    email = 'demo@example.com'
    password = 'DemoPass123!'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = False
        user.save()


def remove_demo_user(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.filter(username='demo_staff').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0006_remove_donationappointment_hospital_name_and_more'),
    ]

    operations = [
        migrations.RunPython(create_demo_user, reverse_code=remove_demo_user),
    ]
