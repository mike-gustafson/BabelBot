from django.db import migrations

def clear_tables(apps, schema_editor):
    Profile = apps.get_model('main_app', 'Profile')
    Translation = apps.get_model('main_app', 'Translation')
    Profile.objects.all().delete()
    Translation.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_remove_request_type'),
    ]

    operations = [
        migrations.RunPython(clear_tables),
    ] 