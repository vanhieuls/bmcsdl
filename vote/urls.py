from django.urls import path, include

from . import views

app_name = "vote"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("candidates/<str:candidate_id>/", views.candidate_detail, name="candidate_detail"),
    path("vote/<str:candidate_id>/", views.vote, name="vote"),
]