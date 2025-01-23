from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)


class Consent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    consent_text = models.TextField(
        help_text="Я даю согласие на обработку моих персональных данных")
    consent_file = models.FileField(
        upload_to='consents/', blank=True, null=True,
        help_text="PDF файл для согласия"
    )
    consent_given = models.BooleanField(default=False,
                                        help_text="Пользователь дал согласие")
    given_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Согласие от {self.user} "
                f"датируемое {self.given_at} ")


class StorageRate(models.Model):
    VOLUME_CHOICES = [
        ('small', 'До 1 м³'),
        ('medium', 'От 1 до 5 м³'),
        ('large', 'Больше 5 м³'),
    ]

    volume_category = models.CharField(
        max_length=10, choices=VOLUME_CHOICES, unique=True,
        verbose_name="Категория объёма"
    )
    cost_per_day = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Стоимость (₽/день)"
    )

    class Meta:
        verbose_name = "Тариф хранения"
        verbose_name_plural = "Тарифы хранения"

    def __str__(self):
        return (f"{self.get_volume_category_display()} -" 
                f" {self.cost_per_day} ₽/день")


class PickupLocation(models.Model):
    address = models.CharField(verbose_name="адрес",
                               max_length=200,
                               blank=True)
    latitude = models.FloatField(verbose_name="широта",
                                 null=True)
    longitude = models.FloatField(verbose_name="долгота",
                                  null=True)

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"

    def __str__(self):
        return f"Точка самовывоза: {self.address}"


class Contract(models.Model):
    owner_name = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='имя владельца',
        related_name='owner_name_contracts'
    )
    owner_phone = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='телефон владельца',
        related_name='owner_phone_contracts'
    )
    storage_rate = models.ForeignKey(
        StorageRate, on_delete=models.CASCADE,
        verbose_name='тариф хранения',
        related_name='contracts'
    )
    start_date = models.DateField(null=True,
                                  verbose_name='дата начала хранения')
    expiration_date = models.DateField(null=True,
                                       verbose_name='дата окончания хранения')
    qr_code = models.BooleanField(default=False,
                                  verbose_name='был ли запрошен QR-код')
    place = models.ForeignKey(
        PickupLocation, on_delete=models.CASCADE,
        verbose_name='место хранения',
        related_name='contracts'
    )

    class Meta:
        verbose_name = "Договор хранения"
        verbose_name_plural = "Договора хранения"

    def __str__(self):
        return (f'Заказ от {self.owner_name}, дата конца хранения: '
                f'{self.expiration_date}')
    

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
