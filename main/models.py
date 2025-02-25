import os

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from main.validators import validate_phone_number

admin.site.site_header = 'Администрирование отелей'


class Room(models.Model):
    number_room = models.CharField(max_length=50, verbose_name='Номер комнаты')
    seat_number = models.CharField(max_length=40, verbose_name='Номер места', default='доп')  # Значение по умолчанию
    occupied = models.BooleanField(default=False, verbose_name='Занята')

    def get_occupied_by_name(self):
        main_table_entry = MainTable.objects.filter(room=self, room__occupied=True).first()
        if main_table_entry:
            url = reverse("admin:main_maintable_change", args=[main_table_entry.id])
            return format_html('<a href="{}">{}</a>', url, main_table_entry.name)
        return "-"

    get_occupied_by_name.short_description = 'Кем'

    def clean(self):
        if not self.pk and self.seat_number != 'доп':
            if Room.objects.filter(number_room=self.number_room, seat_number=self.seat_number).exists():
                raise ValidationError(f"Место {self.seat_number} в комнате {self.number_room} уже существует.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number_room} (Место: {self.seat_number})"

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'


class MainTable(models.Model):

    def user_photo_path(instance, filename):
        name, ext = os.path.splitext(filename)
        new_name = slugify(name)
        return f'user_photo/{new_name}{ext}'

    PAYMENT_CHOICES = {
        "КР": "Карта",
        "НЛ": "Наличные",
        "БН": "Безнал",
    }

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Комната')
    name = models.CharField(max_length=90, verbose_name='ФИО')
    nationality = models.CharField(max_length=50, verbose_name='Регистрация')
    check_in_date = models.DateField(verbose_name='Дата заселения')
    summ = models.PositiveIntegerField(verbose_name='Сумма оплаты')
    check_out_date = models.DateField(verbose_name='Дата выселения')
    payment_method = models.CharField(max_length=3, choices=PAYMENT_CHOICES, verbose_name='Способ оплаты')
    number_phone = models.CharField(max_length=50, verbose_name='Номер телефона', validators=[validate_phone_number])
    organization = models.CharField(max_length=50, verbose_name='Организация', null=True, blank=True)
    photo = models.ImageField(upload_to=user_photo_path, verbose_name='Фото паспорта', null=True, blank=True,)
    description = models.TextField(max_length=300, verbose_name='Примечание', null=True, blank=True)
    update_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменений')
    name_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Администратор')

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = MainTable.objects.get(pk=self.pk)
            if old_instance.room != self.room:
                if old_instance.room:
                    old_instance.room.occupied = False
                    old_instance.room.save()
                if self.room:
                    self.room.occupied = True
                    self.room.save()
        else:
            if self.room:
                self.room.occupied = True
                self.room.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.room:
            self.room.occupied = False
            self.room.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Основная таблица'
        verbose_name_plural = 'Основные таблицы'

