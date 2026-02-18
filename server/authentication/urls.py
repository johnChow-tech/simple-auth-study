from django.urls import path

from .views import (
    login_user,  # 导入 login_user
    register_user,
)

urlpatterns = [
    # 路径：api/register/
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),  # 👈 新增这一行
]
