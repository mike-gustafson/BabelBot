from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('main_app', '0014_fix_heroku_schema'),
    ]

    operations = [
        migrations.RunSQL(
            # This is a no-op migration that just ensures the migration state is in sync
            sql='SELECT 1',
            reverse_sql='SELECT 1'
        ),
    ] 