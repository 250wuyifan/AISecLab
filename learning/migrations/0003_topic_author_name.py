from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_topic_author_topic_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='author_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='作者姓名（可自填）'),
        ),
    ]
