from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegisterSerializer


@api_view(["POST"])
@permission_classes([AllowAny])  # 🚩 注册接口必须是公开的
def register_user(request):
    # 1. 把前端传来的原始数据交给安检员 (Serializer)
    serializer = RegisterSerializer(data=request.data)

    # 2. 安检员开始校验数据是否合法
    if serializer.is_valid():
        # 3. 校验通过，调用 create_user 存入数据库
        serializer.save()
        return Response({"message": "用户创建成功！"}, status=status.HTTP_201_CREATED)

    # 4. 校验失败，把具体的错误原因返回给前端 (例如：用户名已存在)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
