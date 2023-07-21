from django.urls import path

from .views import DealView

urlpatterns = [
    path('', DealView.as_view({'post': 'create', 'get': 'list'}), name='deal'),
]
