from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Deal


@receiver(post_delete, sender=Deal)
@receiver(post_save, sender=Deal)
def clear_cache(sender, **kwargs):
    """Очистка кэша при изменении данных в таблице"""
    cache.delete('response_data')
