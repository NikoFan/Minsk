import uuid

from django.contrib.auth.models import User
from django.db import models


User.__str__ = lambda self: self.username
User.REQUIRED_FIELDS = ['email', 'password']


CATEGORIES = (
    ("A", "мотоцикл"), ("B", "легковой авто"), ("C", "грузовой авто")
)


class Document(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="document", verbose_name="Пользователь")
    passport = models.CharField(max_length=32, verbose_name="Серия и номер паспорта")
    driving_license = models.CharField(max_length=32, verbose_name="Номер водительской лицензии")
    driving_category = models.CharField(max_length=2, verbose_name="Категория вождения", choices=CATEGORIES)
    approved = models.BooleanField(default=False, verbose_name="Подтвержден")

    def __str__(self):
        return f"Документы {self.user}"

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class Car(models.Model):

    COLORS = (
        ("red", "красный"), ("white", "белый"), ("black", "черный")
    )
    MODELS = (
        ("moskvich", "Москвич"),
    )

    state_number = models.CharField(verbose_name="Номера", max_length=6, unique=True, primary_key=True)
    gps_mac_address = models.CharField(verbose_name="Мак-адрес GPS", max_length=32, unique=True)
    model = models.CharField(max_length=64, verbose_name="Модель", choices=MODELS)
    category = models.CharField(max_length=2, verbose_name="Категория авто", choices=CATEGORIES)
    color = models.CharField(max_length=16, verbose_name="Цвет", choices=COLORS)
    park_address = models.TextField(verbose_name="Адрес автопарка")

    def __str__(self):
        return f"Авто {self.state_number}"

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"


class Order(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="orders", verbose_name="Автомобиль")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="order", verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Дата регистрации")
    driving_start = models.DateTimeField(verbose_name="Дата начала поездки")
    driving_end = models.DateTimeField(verbose_name="Дата окончания поездки", null=True, blank=True)
    success = models.BooleanField(verbose_name="Поездка прошла успешно", null=True, blank=True)

    def __str__(self):
        return f"Заказ №_{self.id}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
