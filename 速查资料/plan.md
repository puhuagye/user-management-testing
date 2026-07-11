# 用户管理系统自动化测试 — 实战项目计划

## 项目目标
构建一个端到端的自动化测试项目，把 Python + Linux + SQL + 接口测试 + Web自动化 全部串在一起。
7月底找工作，简历上有一段能说的项目经历。

## 技术栈
- **后端**: Python Flask（RESTful API）
- **数据库**: MySQL
- **前端**: 简单 HTML 页面（够跑 Selenium 就行）
- **测试框架**: Pytest + Requests（接口测试） + Selenium（Web自动化）
- **测试报告**: pytest-html
- **部署环境**: Linux（WSL2 / 虚拟机）

---

## 第1周（7.1 - 7.7）：环境搭建 & 被测应用部署

**目标**：让一个带数据库的 Web 系统在 Linux 上跑起来

- [x] 准备 Linux 环境（WSL2 + Ubuntu ✅，已有，直接启动）
- [x] 安装 MySQL，建库建表（MySQL 8.0，端口3307，数据库 user_management）
- [x] 用 Flask 写增删改查 API（5个接口，比计划多1个）
- [x] 用 pymysql 连接数据库（PyMySQL 1.2.0 + cryptography）
- [x] 部署到 Linux，用 curl 验证接口（WSL2 成功启动，DB_HOST=192.168.1.5）

**产出**：一个在 **Windows + WSL2/Linux** 双环境都能跑起来的 Web 服务 ✅

> Windows MySQL ← WSL Flask 通过局域网 IP 192.168.1.5:3307 连接
> Windows 启动：`python run.py`
> Linux 启动：`DB_HOST=192.168.1.5 python3 run.py`
> Linux 中 MySQL 用 root@% 授权，允许远程连接

---

## 第2周（7.8 - 7.14）：接口自动化测试

**目标**：用 Python 编写完整的接口自动化测试脚本

- [ ] 搭建 Pytest + Requests 测试框架
- [ ] 编写接口测试用例（正常 + 异常场景）
- [ ] SQL 数据落地校验（创建后查数据库确认）
- [ ] 数据驱动测试（pytest.mark.parametrize）
- [ ] pytest-html 生成测试报告
- [ ] tail -f 查看应用日志定位问题

**产出**：一套能自动跑完、带数据库校验的接口测试脚本

---

## 第3周（7.15 - 7.21）：We
b 自动化 & 端到端串联

**目标**：用 Selenium 自动化操作前端页面

- [ ] 给 Flask 加简单 HTML 前端页面
- [ ] 编写 Selenium UI 自动化用例
- [ ] UI + 接口 + SQL 三层校验
- [ ] 引入 Page Object 模式
- [ ] 接口和 UI 用例统一用 pytest 管理

**产出**：可运行的 UI 自动化测试，与数据库校验打通

---

## 第4周（7.22 - 7.28）：整合优化 & 简历面试

**目标**：让项目完整、可展示

- [ ] 配置管理（.ini 或 .yaml 存放配置）
- [ ] 提交 Git，写好 README
- [ ] 上传 GitHub / Gitee
- [ ] 撰写简历项目经历
- [ ] 准备面试问答

**产出**：GitHub 上的完整项目 + 简历上的项目经历

---

## 项目目录结构

```
py.projet01/
├── app/                    # Flask 被测系统
│   ├── app.py             # Flask 入口
│   ├── models.py          # 数据库模型/操作
│   ├── config.py          # 数据库配置
│   └── templates/         # HTML 模板
│       ├── index.html
│       ├── create.html
│       └── edit.html
├── tests/                  # 测试代码
│   ├── api/               # 接口测试
│   │   ├── conftest.py
│   │   └── test_user_api.py
│   ├── ui/                # UI 自动化测试
│   │   ├── conftest.py
│   │   ├── pages/         # Page Object
│   │   │   ├── base_page.py
│   │   │   ├── login_page.py
│   │   │   └── user_page.py
│   │   └── test_user_ui.py
│   └── common/            # 公共工具
│       ├── db_helper.py   # 数据库验证
│       └── config.py      # 配置管理
├── data/                   # 测试数据文件
│   └── test_data.json
├── reports/                # 测试报告输出
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 简历项目描述（目标）

> **项目名称：用户管理系统自动化测试实战**
>
> - 独立搭建 Linux + MySQL + Flask 被测环境，设计 RESTful API 并用 Python 实现对用户增删改查的接口测试
> - 编写 Pytest + Requests 自动化脚本，结合数据库 SQL 查询进行数据落地校验，覆盖正常与异常场景
> - 基于 Selenium 编写 UI 自动化用例，采用 Page Object 模式，与接口测试、数据库校验形成端到端自动化流程
> - 使用 Git 进行版本管理，整合测试报告，可在 Linux 环境下一键执行

---

## 面试常见问题准备

| 问题 | 准备方向 |
|------|----------|
| 项目中用到了哪些 Linux 命令？ | ssh、ls、cd、mkdir、apt、nohup、tail -f、ps、kill、vim |
| SQL 校验具体怎么写的？ | 连接数据库 → 执行 SELECT → assert 比对 |
| 接口测试怎么设计用例？ | 状态码、响应体、数据库落库、边界值 四个维度 |
| 自动化框架结构是怎样的？ | 分层：common层、用例层、数据层 |
| UI 元素定位不到怎么办？ | 显式等待、换定位方式、检查 iframe |
| Page Object 模式是什么？ | 页面元素和操作封装成类，用例不直接写 find_element |
