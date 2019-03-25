# Generated by Django 2.0.7 on 2019-03-14 09:51

from django.db import migrations, connection
from django.db.utils import ProgrammingError


def forwards(apps, schema_editor):

    sql = """
    UPDATE workflow_coreuser AS cu
    SET username = u.username,
        first_name = u.first_name,
        last_name = u.last_name,
        email = u.email,
        is_staff = u.is_staff,
        is_active = u.is_active,
        is_superuser = u.is_superuser,
        last_login = u.last_login,
        "password" = u.password,
        date_joined = u.date_joined
    FROM auth_user AS u
    WHERE cu.user_id = u.id
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
    except ProgrammingError:
        pass


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0010_coreuser_is_active'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
