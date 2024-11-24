# Generated by Django 5.1.2 on 2024-11-24 09:29

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('state_number', models.CharField(max_length=6, primary_key=True, serialize=False, unique=True, verbose_name='Номера')),
                ('gps_mac_address', models.CharField(max_length=32, unique=True, verbose_name='Мак-адрес GPS')),
                ('model', models.CharField(choices=[('moskvich', 'Москвич')], max_length=64, verbose_name='Модель')),
                ('category', models.CharField(choices=[('A', 'мотоцикл'), ('B', 'легковой авто'), ('C', 'грузовой авто')], max_length=2, verbose_name='Категория авто')),
                ('color', models.CharField(choices=[('red', 'красный'), ('white', 'белый'), ('black', 'черный')], max_length=16, verbose_name='Цвет')),
                ('park_address', models.TextField(verbose_name='Адрес автопарка')),
            ],
            options={
                'verbose_name': 'Автомобиль',
                'verbose_name_plural': 'Автомобили',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passport', models.CharField(max_length=32, verbose_name='Серия и номер паспорта')),
                ('driving_license', models.CharField(max_length=32, verbose_name='Номер водительской лицензии')),
                ('driving_category', models.CharField(choices=[('A', 'мотоцикл'), ('B', 'легковой авто'), ('C', 'грузовой авто')], max_length=2, verbose_name='Категория вождения')),
                ('approved', models.BooleanField(default=False, verbose_name='Подтвержден')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='document', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата регистрации')),
                ('driving_start', models.DateTimeField(verbose_name='Дата начала поездки')),
                ('driving_end', models.DateTimeField(verbose_name='Дата окончания поездки')),
                ('success', models.BooleanField(blank=True, null=True, verbose_name='Поездка прошла успешно')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='carsharing.car', verbose_name='Автомобиль')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
    ]
