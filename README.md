# 用户管理系统 — 自动化测试实战项目

一个完整的端到端自动化测试项目：从环境搭建、接口测试、UI 自动化到数据库校验，覆盖企业级测试的核心技能。

## 技术栈

| 层次 | 技术 | 用途 |
|------|------|------|
| 被测应用 | Python Flask | RESTful API（5个接口）+ HTML 前端（3个页面） |
| 数据库 | MySQL 8.0 | 用户数据存储（PyMySQL 连接） |
| 接口测试 | Pytest + Requests | 13 条接口自动化用例，覆盖正常+异常场景 |
| UI 测试 | Selenium (Edge) | 8 条 Web 自动化用例，Page Object 模式 |
| 测试报告 | pytest-html | 一条命令生成 HTML 报告 |
| 配置管理 | YAML + 环境变量 | 配置集中管理，环境变量覆盖 |
| 部署环境 | Windows + WSL2 (Ubuntu) | 双环境支持 |

## 项目结构

```
py.projet01/
├── app/                        # Flask 被测系统
│   ├── app.py                  # 路由层（5个 API + 3个页面路由）
│   ├── models.py               # 数据访问层（CRUD 操作）
│   ├── config.py               # 应用配置（读 config.yaml）
│   └── templates/              # HTML 前端页面
│       ├── index.html          # 用户列表页
│       ├── create.html         # 新增用户页
│       └── edit.html           # 编辑用户页
│
├── tests/                      # 自动化测试代码
│   ├── conftest.py             # 公共 fixtures（db, api_session, cleaning）
│   ├── api/                    # 接口测试
│   │   ├── conftest.py
│   │   └── test_user_api.py    # 13 条接口用例
│   ├── ui/                     # UI 自动化测试
│   │   ├── conftest.py         # Edge WebDriver fixture
│   │   ├── pages/              # Page Object 层
│   │   │   ├── base_page.py    # 基类（封装 click/type/wait）
│   │   │   └── user_page.py    # 页面对象（元素定位+操作）
│   │   └── test_user_ui.py     # 8 条 UI 用例
│   └── common/                 # 公共工具
│       ├── config.py           # 测试配置（读 config.yaml）
│       └── db_helper.py        # 数据库直连校验器
│
├── config.yaml                 # 统一配置文件（唯一配置来源）
├── requirements.txt            # Python 依赖包
├── pytest.ini                  # pytest 配置（日志/标记/发现规则）
├── run.py                      # Flask 启动入口
└── README.md                   # 本文件
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 8.0（端口 3307）
- Microsoft Edge 浏览器（UI 测试用，系统自带）

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `config.yaml`，修改数据库连接信息：

```yaml
database:
  host: 127.0.0.1
  port: 3307
  user: root
  password: "你的密码"
  database: user_management
```

建库建表：

```sql
CREATE DATABASE IF NOT EXISTS user_management;
USE user_management;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) DEFAULT '',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 启动应用

```bash
python run.py
# 访问 http://127.0.0.1:5000
```

### 5. 运行测试

```bash
# 跑全部接口测试（需要先启动 Flask）
pytest tests/api/ -v --html=reports/api_report.html --self-contained-html

# 跑全部 UI 测试（需要先启动 Flask）
pytest tests/ui/ -v --html=reports/ui_report.html --self-contained-html

# 一条命令跑全部 21 条测试
pytest tests/api/ tests/ui/ -v --html=reports/full_report.html --self-contained-html

# 无头模式（不弹浏览器窗口，适合 CI/CD）
pytest tests/ui/ -v --headless
```

## 测试用例覆盖

### 接口测试（13 条）

| 接口 | 用例 | 校验维度 |
|------|------|----------|
| GET /api/users | 查询全部用户 | 状态码 + 响应结构 |
| GET /api/users/\<id\> | 查存在/不存在的用户 | 状态码 + 数据库落地校验 |
| POST /api/users | 正常创建 | HTTP状态 + 业务码 + 数据库落地校验 |
| POST /api/users | 缺必填字段（parametrize × 2） | 400 + 错误提示关键字 |
| POST /api/users | 空请求体 | 400 |
| PUT /api/users/\<id\> | 正常修改 | HTTP状态 + 二次查询确认 |
| PUT /api/users/\<id\> | 修改不存在/空请求体 | 404 / 400 |
| DELETE /api/users/\<id\> | 正常删除 | HTTP状态 + 二次查询确认 |
| DELETE /api/users/\<id\> | 删除不存在/重复删除 | 404 |

### UI 测试（8 条）

| 页面 | 用例 | 校验维度 |
|------|------|----------|
| 用户列表页 | 页面加载、空数据提示 | 元素可见性 |
| 新增用户页 | 正常创建 | UI → API → DB 三层校验 |
| 新增用户页 | 缺姓名/缺邮箱拦截 | 前端校验提示 |
| 编辑页 | 页面加载 + 数据预填 | 输入框 value 验证 |
| 删除操作 | 确认删除 / 取消删除 | alert 弹窗处理 |

## 核心亮点（面试可说）

1. **三层校验**：UI 操作 → API 二次确认 → 数据库直连验证，不以接口返回为准，以数据库状态为准
2. **Page Object 模式**：页面元素定位和操作封装成类，前端改 HTML 只需要改 Page Object 层
3. **Fixture 管理测试生命周期**：session 级别复用数据库连接，function 级别保证用例隔离，yield 实现自动清理
4. **配置集中管理**：config.yaml 统一管理所有配置，环境变量覆盖机制支持多环境切换
5. **数据驱动测试**：@pytest.mark.parametrize 一份代码覆盖多组数据，消除重复
6. **显式等待**：UI 测试用 WebDriverWait + expected_conditions，不盲等 time.sleep
