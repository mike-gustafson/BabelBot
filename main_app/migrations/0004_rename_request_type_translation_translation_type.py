from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_add_translation_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='translation',
            name='request_type',
        ),
        migrations.AddField(
            model_name='translation',
            name='translation_type',
            field=models.CharField(choices=[('typed', 'Typed')], default='typed', max_length=10),
        ),
    ] 