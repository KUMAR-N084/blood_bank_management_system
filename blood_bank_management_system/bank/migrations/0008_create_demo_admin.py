from django.db import migrations


def create_demo_accounts(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # 1. Create demo_admin superuser (full admin access)
    if not User.objects.filter(username='demo_admin').exists():
        User.objects.create_superuser(
            username='demo_admin',
            email='admin@bloodbank.demo',
            password='DemoPass123!',
        )

    # 2. Upgrade existing demo_staff to superuser so they can also access /admin/
    try:
        staff = User.objects.get(username='demo_staff')
        staff.is_superuser = True
        staff.save()
    except User.DoesNotExist:
        pass

    # 3. Create demo_user (regular public user for testing)
    if not User.objects.filter(username='demo_user').exists():
        User.objects.create_user(
            username='demo_user',
            email='user@bloodbank.demo',
            password='DemoPass123!',
        )


def remove_demo_accounts(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.filter(username__in=['demo_admin', 'demo_user']).delete()
    # Revert demo_staff superuser flag
    try:
        staff = User.objects.get(username='demo_staff')
        staff.is_superuser = False
        staff.save()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0007_create_demo_user'),
    ]

    operations = [
        migrations.RunPython(create_demo_accounts, reverse_code=remove_demo_accounts),
    ]
