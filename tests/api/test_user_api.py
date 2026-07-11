"""
用户管理接口测试
================
测试 5 个 REST API 的正常和异常场景。
依赖 conftest.py 里定义的 4 个 fixture：
  db           → 数据库校验器（直接查 MySQL 确认数据落地）
  api_session  → HTTP 会话（复用 TCP 连接，统一 JSON header）
  base_url     → 被测地址（http://127.0.0.1:5000）
  created_ids  → 测试数据清理列表（跑完自动从数据库删除）

面试可以说：
  - 每个接口覆盖正常+异常，异常包含参数缺失、格式错误、资源不存在
  - 接口测试不止看返回状态码，还直接查数据库做"落地校验"
  - 用 created_ids 自动清理，保证测试可重复执行
  - 用 parametrize 做数据驱动，一份代码覆盖多组数据
"""
import pytest
#  ↑ pytest = 测试框架，提供 @pytest.mark.parametrize 等


# ============================================================
# 接口①：GET /api/users — 查全部用户
# ============================================================
class TestUserList:
    """测试 GET /api/users — 查全部用户"""

    def test_list_users_empty_or_not(self, api_session, base_url):
        """
        测试：查全部用户接口
        验证点：
          1. HTTP 状态码是 200
          2. 返回的 JSON 结构正确（code=200, data 是列表）
        """
        url = f"{base_url}/api/users"
        resp = api_session.get(url)

        assert resp.status_code == 200

        result = resp.json()
        assert result["code"] == 200
        assert result["message"] == "查询成功"
        assert isinstance(result["data"], list)

    def test_get_user_by_id_exists(self, api_session, base_url, created_ids, db):
        """
        测试：查一个存在的用户
        步骤：
          1. 先创建一个用户（拿到 ID）
          2. 再查这个用户（验证能查到）
          3. 查数据库确认数据落地
        验证点：
          1. 状态码 200
          2. 返回的用户信息正确
          3. 数据库里确实有这条数据
        """
        # 第1步：先造一个用户（POST 创建）
        create_resp = api_session.post(
            f"{base_url}/api/users",
            json={
                "name": "查询测试",
                "email": "query_test@test.com",
            },
        )
        create_result = create_resp.json()
        assert create_resp.status_code == 200
        assert create_result["code"] == 201
        new_id = create_result["data"]["id"]
        created_ids.append(new_id)  # 立即登记清理

        # 第2步：查这个用户
        resp = api_session.get(f"{base_url}/api/users/{new_id}")

        # 第3步：验证
        assert resp.status_code == 200
        result = resp.json()
        assert result["code"] == 200
        assert result["data"]["name"] == "查询测试"
        assert result["data"]["email"] == "query_test@test.com"

        # 第4步：数据库落地校验（绕过接口，直接查 MySQL）
        user_in_db = db.get_user_by_id(new_id)
        assert user_in_db is not None
        assert user_in_db["name"] == "查询测试"
        assert user_in_db["email"] == "query_test@test.com"

    def test_get_user_by_id_not_found(self, api_session, base_url):
        """
        测试：查一个不存在的用户（异常场景）
        验证点：code=404，data=None
        """
        resp = api_session.get(f"{base_url}/api/users/99999")

        assert resp.status_code == 200

        result = resp.json()
        assert result["code"] == 404
        assert result["message"] == "用户不存在"
        assert result["data"] is None


# ============================================================
# 接口③：POST /api/users — 新增用户
# ============================================================
class TestUserCreate:
    """测试 POST /api/users — 新增用户"""

    def test_create_user_success(self, api_session, base_url, created_ids, db):
        """
        测试：正常创建用户（只传必填字段 name + email）
        验证点：
          1. HTTP 状态码 200
          2. 业务 code 是 201
          3. 返回的 data 里有 id
          4. 数据库里真的有这条数据（落地校验）
        """
        resp = api_session.post(
            f"{base_url}/api/users",
            json={
                "name": "正常创建",
                "email": "normal_create@test.com",
            },
        )
        result = resp.json()

        # 立刻登记清理（写在 assert 前面，防止 assert 失败后数据残留）
        new_id = result["data"]["id"]
        created_ids.append(new_id)

        # HTTP + 业务状态
        assert resp.status_code == 200
        assert result["code"] == 201
        assert result["message"] == "用户创建成功"
        assert result["data"]["id"] is not None
        assert isinstance(result["data"]["id"], int)

        # 数据库落地校验
        user = db.get_user_by_id(new_id)
        assert user is not None, f"数据库里没找到 ID={new_id} 的用户！"
        assert user["name"] == "正常创建"
        assert user["email"] == "normal_create@test.com"

    # ── 数据驱动：缺少必填字段 ──
    @pytest.mark.parametrize(
        "payload,keyword",
        [
            pytest.param({"email": "no_name@test.com"}, "姓名", id="缺name"),
            pytest.param({"name": "没邮箱"}, "邮箱", id="缺email"),
        ],
    )
    def test_create_user_missing_field(self, api_session, base_url, payload, keyword):
        """
        测试：创建用户时缺少必填字段（数据驱动）
        parametrize 会把两组数据分别注入，跑两轮：
          第 1 轮：payload={"email":"..."}  keyword="姓名"  → 测缺 name
          第 2 轮：payload={"name":"..."}   keyword="邮箱"  → 测缺 email

        好处：一份代码跑多组数据，新增场景只加参数不加代码
        """
        resp = api_session.post(
            f"{base_url}/api/users",
            json=payload,   # ← 每轮不同
        )
        result = resp.json()

        assert resp.status_code == 200
        assert result["code"] == 400
        assert result["data"] is None
        assert keyword in result["message"]   # ← 每轮不同

    def test_create_user_empty_body(self, api_session, base_url):
        """
        测试：请求体为空 JSON 对象（异常场景）
        验证点：code=400，提示"请求体不能为空"
        """
        resp = api_session.post(f"{base_url}/api/users", json={})
        result = resp.json()

        assert resp.status_code == 200
        assert result["code"] == 400
        assert "请求体不能为空" in result["message"]


# ============================================================
# 接口④：PUT /api/users/<id> — 修改用户
# ============================================================
class TestUserUpdate:
    """测试 PUT /api/users/<id> — 修改用户"""

    def test_update_user_name(self, api_session, base_url, created_ids):
        """
        测试：正常修改用户姓名
        步骤：创建 → 修改 → 再查一次确认
        验证点：二次查询时 name 已变成新值（落地校验）
        """
        # 第1步：创建用户
        create_resp = api_session.post(
            f"{base_url}/api/users",
            json={"name": "改前", "email": "update_test@test.com"},
        )
        user_id = create_resp.json()["data"]["id"]
        created_ids.append(user_id)

        # 第2步：修改姓名
        update_resp = api_session.put(
            f"{base_url}/api/users/{user_id}",
            json={"name": "改后"},
        )
        update_result = update_resp.json()

        assert update_resp.status_code == 200
        assert update_result["code"] == 200
        assert update_result["message"] == "修改成功"

        # 第3步：再查一次确认（不只看接口说"改好了"，要真的查）
        get_resp = api_session.get(f"{base_url}/api/users/{user_id}")
        get_result = get_resp.json()
        assert get_result["data"]["name"] == "改后"

    def test_update_user_not_found(self, api_session, base_url):
        """
        测试：修改不存在的用户（异常场景）
        验证点：code=404
        """
        resp = api_session.put(
            f"{base_url}/api/users/99999",
            json={"name": "改了也白改"},
        )
        result = resp.json()

        assert resp.status_code == 200
        assert result["code"] == 404
        assert result["data"] is None
        assert "用户不存在" in result["message"]

    def test_update_user_empty_body(self, api_session, base_url, created_ids):
        """
        测试：修改用户时传空 JSON（异常场景）
        验证点：code=400
        """
        # 先创建用户拿到真实 ID
        create_resp = api_session.post(
            f"{base_url}/api/users",
            json={"name": "测试空修改", "email": "empty_update@test.com"},
        )
        user_id = create_resp.json()["data"]["id"]
        created_ids.append(user_id)

        # 发空 JSON 修改
        resp = api_session.put(f"{base_url}/api/users/{user_id}", json={})
        result = resp.json()

        assert resp.status_code == 200
        assert result["code"] == 400
        assert "请求体不能为空" in result["message"]


# ============================================================
# 接口⑤：DELETE /api/users/<id> — 删除用户
# ============================================================
class TestUserDelete:
    """测试 DELETE /api/users/<id> — 删除用户"""

    def test_delete_user_success(self, api_session, base_url, created_ids):
        """
        测试：正常删除用户
        步骤：创建 → 删除 → 再查确认查不到
        验证点：再次查询返回 404（已删除）
        """
        # 第1步：创建
        create_resp = api_session.post(
            f"{base_url}/api/users",
            json={"name": "待删除", "email": "delete_test@test.com"},
        )
        user_id = create_resp.json()["data"]["id"]
        created_ids.append(user_id)

        # 第2步：删除
        delete_resp = api_session.delete(f"{base_url}/api/users/{user_id}")
        delete_result = delete_resp.json()

        assert delete_resp.status_code == 200
        assert delete_result["code"] == 200
        assert delete_result["message"] == "删除成功"

        # 第3步：再查确认真的删了
        get_resp = api_session.get(f"{base_url}/api/users/{user_id}")
        get_result = get_resp.json()
        assert get_result["code"] == 404
        assert "用户不存在" in get_result["message"]

        # 第4步：从清理列表移除（已经自己删了，不用 fixture 再删）
        created_ids.remove(user_id)

    def test_delete_user_not_found(self, api_session, base_url):
        """
        测试：删除不存在的用户（异常场景）
        验证点：code=404
        """
        resp = api_session.delete(f"{base_url}/api/users/99999")
        result = resp.json()

        assert resp.status_code == 200
        assert result["code"] == 404
        assert result["data"] is None
        assert "用户不存在" in result["message"]

    def test_delete_user_twice(self, api_session, base_url, created_ids):
        """
        测试：对同一用户删除两次（幂等性检查）
        验证点：第一次成功 200，第二次 404
        """
        # 第1步：创建
        create_resp = api_session.post(
            f"{base_url}/api/users",
            json={"name": "删两次", "email": "delete_twice@test.com"},
        )
        user_id = create_resp.json()["data"]["id"]
        # 不用 created_ids！自己手动删，不让 fixture 再多删一次

        # 第2步：第一次删除 → 成功
        resp1 = api_session.delete(f"{base_url}/api/users/{user_id}")
        result1 = resp1.json()
        assert result1["code"] == 200

        # 第3步：第二次删除 → 用户不存在
        resp2 = api_session.delete(f"{base_url}/api/users/{user_id}")
        result2 = resp2.json()
        assert result2["code"] == 404
        assert "用户不存在" in result2["message"]
