from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class RegisterAPITests(APITestCase):
    """
    [QA 视角] 注册接口自动化测试套件
    APITestCase 会在每次运行测试时，自动建一个纯净的“内存数据库”。
    测试跑完，数据库销毁。绝对不会污染你的 db.sqlite3！
    """

    def setUp(self):
        # setUp 相当于测试的前置准备（Test Setup）
        # 这里为了极简，我们直接写死 URL。如果 urls.py 里配了 name='register'，可以使用 reverse('register')
        self.url = "/api/register/"
        self.valid_payload = {
            "username": "tester001",
            "password": "StrongPassword123!",
            "email": "tester@example.com",
        }

    def test_register_happy_path_and_db_audit(self):
        """
        用例 1：正常注册流程与白盒数据审计（核心！）
        """
        # 1. 模拟前端发送 POST 请求
        response = self.client.post(self.url, self.valid_payload, format="json")

        # 2. [黑盒断言] 检查接口状态码
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. [白盒断言] 穿透到底层，检查数据库里是不是真的多了一个人
        self.assertEqual(User.objects.count(), 1)

        # 4. [安全审计断言] 捞出这个用户，检查密码是否被正确哈希！
        user = User.objects.get(username="tester001")
        # 绝对不能是明文！
        self.assertNotEqual(user.password, "StrongPassword123!")
        # 验证哈希值是否能和原密码匹配（验证 create_user 是否工作正常）
        self.assertTrue(user.check_password("StrongPassword123!"))

    def test_register_missing_required_fields(self):
        """
        用例 2：异常流 - 必填项缺失校验
        测试 Serializer 的安检能力是否在线
        """
        # 故意不传 password
        bad_payload = {"username": "hacker_no_pwd"}
        response = self.client.post(self.url, bad_payload, format="json")

        # 断言状态码必须是 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 断言报错信息里必须明确指出是 password 出了问题
        response_body = response.json()
        self.assertIn("password", response_body)
        # 白盒断言：数据库里绝对不能有脏数据落盘
        self.assertEqual(User.objects.count(), 0)

    def test_register_duplicate_username(self):
        """
        用例 3：异常流 - 违反唯一性约束
        """
        # 先手动在测试数据库里“埋”一个老用户
        User.objects.create_user(username="tester001", password="OldPassword")

        # 尝试用同样的 username 注册
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_body = response.json()
        self.assertIn("username", response_body)
        # 验证数据库没有增加新数据，依然只有刚才埋的那 1 个
        self.assertEqual(User.objects.count(), 1)
