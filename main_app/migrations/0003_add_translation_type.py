from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_rename_target_lang_translation_target_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='translation',
            name='translation_type',
            field=models.CharField(choices=[('typed', 'Typed')], default='typed', max_length=10),
        ),
    ] 