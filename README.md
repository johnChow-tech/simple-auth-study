# 🛡️ Simple Auth Study (MVP)

这是一个专为 **白盒测试学习** 设计的极简前后端分离项目。

* **后端**：Django + DRF + JWT
* **前端**：React + TypeScript + Vite

---

## 🏗️ 环境搭建指南

### 1. 后端设置 (Server)

进入 `server` 文件夹，这里是数据的核心加工厂。

1. **创建虚拟环境**：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **安装依赖**：
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv
```

3. **配置环境变量**：
* 在 `server/` 目录下新建 `.env` 文件。
* 写入 `DJANGO_SECRET_KEY=你的随机密钥`。

4. **初始化数据库**：
```bash
python manage.py migrate
```

5. **启动服务**：
```bash
python manage.py runserver
```

### 2. 前端设置 (Client)

进入 `client` 文件夹，这里是用户交互的门户。

1. **安装依赖**：
```bash
npm install
```

2. **启动开发服务器**：
```bash
npm run dev
```

访问地址通常为：`http://localhost:5173`