from django.urls import path

from . import views

app_name = "savings"

urlpatterns = [
    path("dev-login/", views.dev_login, name="dev_login"),
    path("", views.dashboard, name="dashboard"),
    path("save/", views.create_saving, name="create_saving"),
    path("reward/", views.create_reward, name="create_reward"),
    path("save/<int:pk>/delete/", views.delete_saving, name="delete_saving"),
    path("reward/<int:pk>/delete/", views.delete_reward, name="delete_reward"),
]
