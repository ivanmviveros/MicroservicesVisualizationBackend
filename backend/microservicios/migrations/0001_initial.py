# Generated by Django 4.0.8 on 2023-03-14 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Microservicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_id', models.IntegerField()),
                ('historias', models.TextField()),
            ],
        ),
    ]
