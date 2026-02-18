from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    # [QA 审计]：必须声明 password 为 write_only！
    # 否则注册成功的 Response 里会带上用户的密码哈希，造成信息泄露。
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        # [QA 审计]：绝对不能用 User.objects.create()！
        # 必须用 create_user，它内部封装了 PBKDF2 算法的哈希逻辑。
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
        )
        return user
