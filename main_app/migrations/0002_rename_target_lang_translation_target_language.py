from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='translation',
            old_name='target_lang',
            new_name='target_language',
        ),
    ] 