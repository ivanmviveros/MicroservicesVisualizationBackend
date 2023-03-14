# Generated by Django 4.0.8 on 2023-03-14 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Configuracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_proyecto', models.CharField(max_length=100)),
                ('cantidad_microservicios', models.IntegerField()),
                ('cantidad_historias', models.IntegerField()),
                ('json_info', models.TextField()),
            ],
        ),
    ]