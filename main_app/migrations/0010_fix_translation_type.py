from django.db import migrations, models

def set_translation_type_default(apps, schema_editor):
    Translation = apps.get_model('main_app', 'Translation')
    Translation.objects.filter(translation_type__isnull=True).update(translation_type='typed')

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_fix_heroku_is_anonymous'),
    ]

    operations = [
        migrations.RunPython(set_translation_type_default),
        migrations.AlterField(
            model_name='translation',
            name='translation_type',
            field=models.CharField(max_length=10, choices=[('typed', 'Typed')], default='typed'),
        ),
    ] 