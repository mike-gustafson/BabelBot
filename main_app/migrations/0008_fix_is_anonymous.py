from django.db import migrations, models

def set_is_anonymous_default(apps, schema_editor):
    Profile = apps.get_model('main_app', 'Profile')
    Profile.objects.filter(is_anonymous__isnull=True).update(is_anonymous=False)

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_alter_profile_is_anonymous'),
    ]

    operations = [
        migrations.RunPython(set_is_anonymous_default),
        migrations.AlterField(
            model_name='profile',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ] 