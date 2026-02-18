from django.contrib.auth import authenticate  # 核心比对工具
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,  # 🚩 导入这个保安
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken  # JWT 签发工具

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


@api_view(["POST"])
@permission_classes([AllowAny])  # 登录接口也必须是公开的
def login_user(request):
    # 1. 获取前端传来的账号密码
    username = request.data.get("username")
    password = request.data.get("password")

    # [QA 审计点 1]：入参非空校验
    if not username:
        return Response({"error": "请提供用户名"}, status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return Response({"error": "请提供密码"}, status=status.HTTP_400_BAD_REQUEST)

    # 2. 核心验证逻辑
    # authenticate 会去数据库捞出这个用户，并将传入的明文 password 进行哈希计算
    # 然后比对两个哈希值。如果匹配，返回 User 对象；如果不匹配，返回 None
    user = authenticate(username=username, password=password)

    # 3. 结果分支处理
    if user is not None:
        # [QA 审计点 2]：签发 JWT Token
        # 只要代码走到这里，说明密码对了。我们给这个用户生成一套 Token。
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "登录成功",
                "user": user.username,
                "tokens": {
                    "refresh": str(refresh),  # 刷新令牌（长期有效）
                    "access": str(
                        refresh.access_token
                    ),  # 访问令牌（短期有效，通常5-15分钟）
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        # [QA 审计点 3]：模糊报错原则
        # 即使是账号不存在，或者密码错误，我们都统一返回“凭证无效”
        return Response(
            {"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED
        )


"""
🚨 担忧 1：防御暴力破解（Brute Force）
黑客视角：既然接口没有验证码，也没有调用频率限制（Rate Limiting），那我是不是可以写个脚本，对着 admin 这个账号，一秒钟试 1000 个密码？

QA 审计结论：当前代码完全裸奔，没有任何防爆破机制（比如“密码错误 5 次锁定账号 15 分钟”）。在真实业务中，这是 P0 级别的安全漏洞。

🚨 担忧 2：“模糊报错”的安全哲学
代码逻辑：你看代码的最后一行，我写的是 用户名或密码错误。

为什么不写“该用户不存在”？：如果后端明确告诉前端“用户不存在”，黑客就可以利用这个接口，批量跑字典，“爆破”出你们系统里到底注册了哪些用户名（这叫 User Enumeration 攻击）。统一报错是白盒审计的铁律。

🚨 担忧 3：JWT 的“覆水难收”
JWT 的致命弱点：一旦 access_token 被签发并发送给前端，在它过期（比如 15 分钟）之前，后端没有任何简单的办法让它强制失效。

QA 脑洞场景：假设用户 A 登录了，拿到了 Token。半分钟后，管理员在后台把用户 A 的账号“封禁（Ban）”了。请问，用户 A 手里那个还有 14 分钟才过期的 Token，还能继续访问系统吗？

答案是：如果不做特殊处理，他依然能访问！因为 JWT 的校验是在本地解密计算的，不需要查数据库！
"""


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # 🔒 核心拦截器：没有合法 Token 的，统统挡在门外
def protected_vip_data(request):
    # 只要能走到这一行，说明 DRF 已经帮你验证过 Token，
    # 并且把 Token 里的 user_id 还原成了真实的 user 对象！
    user = request.user

    return Response(
        {
            "message": "欢迎进入 VIP 包厢！",
            "username": user.username,
            "email": user.email,
            "vip_secret": "这是只有登录用户才能看到的绝密财报数据 📈",
        },
        status=status.HTTP_200_OK,
    )
