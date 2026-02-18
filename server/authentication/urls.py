from django.urls import path

from .views import register_user

urlpatterns = [
    # 路径：api/register/
    path("register/", register_user, name="register"),
]
