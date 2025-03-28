from django.urls import path
from . import views

app_name = "news_app"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("foreign_news/", views.ForeignNewsView.as_view(), name="foreign_news"),
    path("nikkei_med/", views.NikkeiMedView.as_view(), name="nikkei_med"),
]