# 毕业设计指导网站

一个前后端分离的毕业设计指导平台，旨在使学生和教师能够通过网络进行毕业设计辅导。

## 项目结构

```
svc/
├── frontend/          # 前端项目 (Vue 3 + Vite)
│   ├── src/
│   │   ├── pages/    # 页面组件
│   │   ├── components/ # 通用组件
│   │   ├── stores/   # Pinia 状态管理
│   │   ├── router/   # 路由配置
│   │   ├── api/      # API 接口
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── backend/          # 后端项目 (Flask + Python)
    ├── app.py        # Flask 应用
    ├── config.py     # 配置文件
    ├── models.py     # 数据库模型
    ├── auth.py       # 认证接口
    ├── requirements.txt
    └── .env.example
```

## 功能特性

### 已实现功能
- ✅ 用户注册 (学生/教师)
- ✅ 用户登录
- ✅ 忘记密码
- ✅ 密码重置
- ✅ 个人信息管理
- ✅ 文件上传/下载
- ✅ 文件管理（编辑、删除、搜索）

### 待实现功能
- ⬜ 问题提问与回答
- ⬜ 教师管理学生
- ⬜ 群发消息
- ⬜ 评价机制
- ⬜ 文档管理

## 快速开始

### 方式一：自动启动（Windows）

双击运行：
```bash
start-all.bat
```

这将自动启动后端和前端，然后在浏览器中打开：`http://localhost:5173`

### 方式二：手动启动

**后端设置**

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/Mac
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动后端服务
```bash
python app.py
```

后端将运行在 `http://localhost:5000`

**前端设置**

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端将运行在 `http://localhost:5173`

### 健康检查

启动后，可以在浏览器中测试API是否正常运行：

```
后端健康检查: http://localhost:5000/api/health
应该返回: {"code": 200, "message": "OK", "status": "healthy"}
```

### 调试

如遇问题，运行状态检查脚本：

```bash
check-status.bat
```

这将检查：
- Python和Node.js版本
- 端口占用情况
- 依赖包安装情况

## API 文档

### 认证接口

#### 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "string (3-80)",
  "email": "string",
  "password": "string (8+, 需含大小写字母和数字)",
  "real_name": "string",
  "user_type": "student|teacher",
  "student_id": "string (学生必填)",
  "teacher_id": "string (教师必填)",
  "college": "string",
  "major": "string (学生必填)",
  "phone": "string"
}

Response: 201 Created
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "user_id": number,
    "username": "string",
    "email": "string"
  }
}
```

#### 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "user": { ... }
  }
}
```

#### 刷新令牌
```
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response: 200 OK
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "string"
  }
}
```

#### 忘记密码
```
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "string"
}

Response: 200 OK
{
  "code": 200,
  "message": "如果该邮箱已注册，您将收到密码重置链接"
}
```

#### 重置密码
```
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "string",
  "password": "string"
}

Response: 200 OK
{
  "code": 200,
  "message": "密码重置成功"
}
```

#### 获取个人信息
```
GET /api/auth/profile
Authorization: Bearer <access_token>

Response: 200 OK
{
  "code": 200,
  "message": "获取成功",
  "data": { ... }
}
```

#### 更新个人信息
```
PUT /api/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "real_name": "string",
  "phone": "string",
  "college": "string",
  "major": "string"
}

Response: 200 OK
{
  "code": 200,
  "message": "更新成功",
  "data": { ... }
}
```

### 文件管理接口

#### 上传文件
```
POST /api/files/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
- file: 文件 (必填)
- description: 文件描述 (可选)
- is_public: 是否公开 (可选，true/false)

Response: 201 Created
{
  "code": 201,
  "message": "文件上传成功",
  "data": { ... }
}
```

#### 获取文件列表
```
GET /api/files/list?page=1&per_page=10
Authorization: Bearer <access_token>

Response: 200 OK
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "files": [...],
    "total": number,
    "pages": number,
    "current_page": number
  }
}
```

#### 下载文件
```
GET /api/files/{file_id}/download
Authorization: Bearer <access_token>

Response: 文件二进制内容
```

#### 删除文件
```
DELETE /api/files/{file_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "code": 200,
  "message": "文件删除成功"
}
```

#### 搜索文件
```
GET /api/files/search?keyword=&file_type=&page=1&per_page=10
Authorization: Bearer <access_token>

Response: 200 OK
{
  "code": 200,
  "message": "搜索成功",
  "data": {
    "files": [...],
    "total": number,
    "pages": number,
    "current_page": number
  }
}
```

## 技术栈

### 前端
- Vue 3
- Vite
- Vue Router 4
- Pinia
- Element Plus
- Axios

### 后端
- Python 3
- Flask
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (JWT认证)
- Flask-CORS (跨域请求)
- SQLite (数据库)

## 安全特性

- JWT 令牌认证
- 密码强度验证 (至少8个字符，需含大小写字母和数字)
- 密码加密存储 (Werkzeug security)
- CORS 跨域保护
- 邮箱格式验证
- 令牌过期机制

## 环境要求

- Node.js 16+
- Python 3.8+
- npm 或 yarn

## 许可证

MIT
