from django.urls import path
from . import views

urlpatterns = [
    path('GetNovelData/', views.NovelScrapingAPIView.as_view()),
   
]
