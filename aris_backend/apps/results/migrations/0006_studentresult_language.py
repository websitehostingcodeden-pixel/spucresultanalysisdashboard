# Generated migration for StudentResult language field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0005_studentresult_subject_marks_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentresult',
            name='language',
            field=models.CharField(
                blank=True,
                null=True,
                max_length=50,
                choices=[
                    ('K', 'Kannada'),
                    ('H', 'Hindi'),
                    ('S', 'Sanskrit'),
                ]
            ),
        ),
    ]
