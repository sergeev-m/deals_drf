from django.db import models
from django.conf import settings


class Customer(models.Model):
    username = models.CharField(
        'Логин покупателя',
        max_length=settings.CUSTOMER_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return self.username


class Gem(models.Model):
    name = models.CharField(
        'Название камня',
        max_length=settings.GEM_NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'

    def __str__(self):
        return self.name


class Deal(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='deals'
    )
    item = models.ForeignKey(
        Gem,
        on_delete=models.CASCADE,
        related_name='deals'
    )
    total = models.PositiveIntegerField('Общая сумма покупки')
    quantity = models.PositiveSmallIntegerField('Количество камней')
    date = models.DateTimeField('Дата покупки')

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    def __str__(self):
        return f'{self.customer} - {self.item} - {self.total}'
