from django.urls import path
from . import views

urlpatterns = [
    path('v1/book/<int:id>/', views.EngineAPIView.as_view(), name='api_test'),
]