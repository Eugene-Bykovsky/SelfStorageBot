from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)

    class Meta:
        app_label = 'handlers'

class Consent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    consent_text = models.TextField(help_text="Я даю согласие на обработку моих персональных данных")
    consent_file = models.FileField(
        upload_to='consents/', blank=True, null=True, help_text="PDF файл для согласия"
    )
    consent_given = models.BooleanField(default=False, help_text="Пользователь дал согласие")
    given_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Согласие от {self.user.email or self.user.username} датируемое {self.given_at}"


class StorageRate(models.Model):
    VOLUME_CHOICES = [
        ('small', 'До 1 м³'),
        ('medium', 'От 1 до 5 м³'),
        ('large', 'Больше 5 м³'),
    ]

    volume_category = models.CharField(
        max_length=10, choices=VOLUME_CHOICES, unique=True, verbose_name="Категория объёма"
    )
    cost_per_day = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Стоимость (₽/день)"
    )

    class Meta:
        verbose_name = "Тариф хранения"
        verbose_name_plural = "Тарифы хранения"

    def __str__(self):
        return f"{self.get_volume_category_display()} - {self.cost_per_day} ₽/день"


class StorageBox(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_boxes')
    size = models.CharField(
        max_length=10, choices=StorageRate.VOLUME_CHOICES, verbose_name="Размер бокса"
    )
    start_date = models.DateField(verbose_name="Дата начала аренды")
    end_date = models.DateField(verbose_name="Дата окончания аренды")
    address = models.TextField(verbose_name="Адрес хранения")
    is_active = models.BooleanField(default=True, verbose_name="Активный бокс")

    def __str__(self):
        return f"Бокс пользователя {self.user.username}: {self.size}"


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    storage_box = models.ForeignKey(StorageBox, on_delete=models.CASCADE, related_name='reminders')
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
