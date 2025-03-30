from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = "news_app"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("foreign_news/", views.ForeignNewsView.as_view(), name="foreign_news"),
    path("nikkei_med/", views.NikkeiMedView.as_view(), name="nikkei_med"),
    path("zizi_med/", views.ZiziMedView.as_view(), name="zizi_med"),
    path("favorite_list/", views.FavoriteListView.as_view(), name="favorite_list"),
    path("add_favorite/", views.AddFavoriteView.as_view(), name="add_favorite"),
    path("update_favorite/<int:pk>/", views.UpdateFavoriteView.as_view(), name="update_favorite"),
    path("delete_favorite/<int:pk>/", views.DeleteFavoriteView.as_view(), name="delete_favorite"),
    ]

