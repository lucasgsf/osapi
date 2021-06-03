from django.urls import path
from .views import CalculoAcaoView

urlpatterns = [
    path('', CalculoAcaoView.as_view())
]