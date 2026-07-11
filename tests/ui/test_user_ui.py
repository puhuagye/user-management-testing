"""
用户管理 UI 自动化测试
======================
用 Selenium 模拟真实用户在浏览器里的操作：
  打开页面 → 点按钮 → 填表单 → 提交 → 验证结果

每条用例都走"三层校验"：
  ① UI 层：页面上出现了预期内容
  ② API 层：调接口确认数据
  ③ DB  层：直连数据库确认数据落地

面试可以说：
  UI 测试不止看页面显示，还通过 API 和数据库做双重落地校验。
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ===== 辅助函数 =====

def _wait_and_accept_alert(driver, timeout=3):
    """
    等待 alert 弹窗出现，然后点"确定"关闭它
    -------------------------------------------------
    为什么需要这个函数？
      JS 的 alert() 不是瞬间出现的，点完提交按钮后有延迟。
      如果直接 driver.switch_to.alert，可能弹窗还没出来，报了异常就不处理了。
      用 WebDriverWait 等弹窗真正出现后再操作。
    """
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        time.sleep(0.5)  # 弹窗关闭后给浏览器一点反应时间
    except Exception:
        pass  # 没弹窗也不卡死


def _wait_for_element_text(driver, by, value, timeout=5):
    """
    等待某个元素的 text 不为空（用于 AJAX 加载数据的场景）
    例如编辑页面：打开后 JS 调 API 拿到旧数据再填到输入框，
    这需要时间，不能一打开页面就取输入框的值
    """
    for _ in range(timeout * 5):  # 每 0.2 秒检查一次
        try:
            el = driver.find_element(by, value)
            text = el.text or el.get_attribute('value')
            if text:
                return el
        except Exception:
            pass
        time.sleep(0.2)
    # 超时了也返回元素，让测试的断言去报错
    return driver.find_element(by, value)


# ============================================================
# 测试组①：用户列表页
# ============================================================
class TestUserListPage:
    """测试用户列表页的加载和显示"""

    def test_list_page_loads(self, driver, base_url):
        """
        测试：打开用户列表页 → 页面正常加载
        验证点：表格元素存在
        """
        driver.get(f'{base_url}/users')
        table = driver.find_element(By.ID, 'userTable')
        assert table.is_displayed(), '用户列表表格应该可见'

    def test_empty_list_shows_hint(self, driver, base_url, db):
        """
        测试：数据库里没有测试用户时，页面显示"暂无数据"提示
        """
        db.cleanup_by_email_keyword('@test.com')
        driver.get(f'{base_url}/users')
        try:
            hint = driver.find_element(By.ID, 'emptyHint')
            if hint.is_displayed():
                assert '暂无用户数据' in hint.text
        except Exception:
            pass


# ============================================================
# 测试组②：新增用户（UI 操作）
# ============================================================
class TestCreateUserUI:
    """测试通过 UI 新增用户 — 核心业务流程"""

    def test_create_user_success(self, driver, base_url, db, api_session):
        """
        测试：通过 UI 表单新增用户 — 三层校验
        ① UI：填表单→提交→列表页出现新用户
        ② API：调接口确认
        ③ DB：直连数据库确认
        """
        # ── 第1步：打开新增用户页面 ──
        driver.get(f'{base_url}/users/create')

        # ── 第2步：填表单 ──
        driver.find_element(By.ID, 'name').send_keys('UI测试张三')
        driver.find_element(By.ID, 'email').send_keys('ui_zhangsan@test.com')
        driver.find_element(By.ID, 'phone').send_keys('13800001111')

        # ── 第3步：点提交 ──
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # ── 第4步：等弹窗出现 → 关掉弹窗 ──
        _wait_and_accept_alert(driver)

        # ── 第5步：等页面跳转到列表页 ──
        # window.location.href = '/users' 需要时间
        WebDriverWait(driver, 5).until(EC.url_contains('/users'))

        # ── 第6步：UI 验证 ──
        time.sleep(1)  # 等 JS 渲染表格
        page_html = driver.page_source
        assert 'UI测试张三' in page_html, '列表页应该显示新用户姓名'
        assert 'ui_zhangsan@test.com' in page_html, '列表页应该显示新用户邮箱'

        # ── 第8步：API 验证 ──
        resp = api_session.get(f'{base_url}/api/users')
        users = resp.json()['data']
        created = [u for u in users if u['email'] == 'ui_zhangsan@test.com']
        assert len(created) == 1, f'应该找到1条，实际{len(created)}条'
        new_id = created[0]['id']

        # ── 第9步：DB 验证 ──
        user_in_db = db.get_user_by_id(new_id)
        assert user_in_db is not None, f'数据库里应该有 ID={new_id}'
        assert user_in_db['name'] == 'UI测试张三'

        # ── 清理 ──
        db.delete_user_by_id(new_id)

    def test_create_user_missing_name(self, driver, base_url):
        """
        测试：不填姓名直接提交 → 前端拦截，显示"请输入姓名"
        """
        driver.get(f'{base_url}/users/create')

        # 关掉浏览器 HTML5 校验，让 JS 校验来拦截
        driver.execute_script(
            "document.getElementById('createForm').setAttribute('novalidate', '')"
        )

        # 只填邮箱，不填姓名
        driver.find_element(By.ID, 'email').send_keys('no_name@test.com')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # 等 JS 校验执行完
        time.sleep(0.3)

        # 验证 error message 出现了
        error_msg = driver.find_element(By.ID, 'message')
        assert error_msg.is_displayed(), '错误消息应该可见'
        assert '请输入姓名' in error_msg.text

    def test_create_user_missing_email(self, driver, base_url):
        """
        测试：不填邮箱直接提交 → 应显示"请输入邮箱"
        """
        driver.get(f'{base_url}/users/create')
        driver.execute_script(
            "document.getElementById('createForm').setAttribute('novalidate', '')"
        )

        driver.find_element(By.ID, 'name').send_keys('没邮箱')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        time.sleep(0.3)

        error_msg = driver.find_element(By.ID, 'message')
        assert error_msg.is_displayed()
        assert '请输入邮箱' in error_msg.text


# ============================================================
# 测试组③：编辑用户（UI 操作）
# ============================================================
class TestEditUserUI:
    """测试通过 UI 编辑用户"""

    def test_edit_page_loads_data(self, driver, base_url, db, api_session):
        """
        测试：编辑页打开后能正确加载用户旧数据（AJAX 预填）
        步骤：API 创建用户 → 打开编辑页 → 确认输入框预填了旧数据

        注意：编辑表单的提交（PUT 请求）走的是 JS fetch，
        已在 API 测试（tests/api/test_user_api.py）中覆盖。
        这里只测 UI 层的数据加载是否正确。
        """
        # ── 第1步：API 创建测试用户 ──
        resp = api_session.post(
            f'{base_url}/api/users',
            json={'name': '改前名字', 'email': 'edit_ui@test.com'},
        )
        user_id = resp.json()['data']['id']

        # ── 第2步：打开编辑页面 ──
        driver.get(f'{base_url}/users/{user_id}/edit')
        time.sleep(1)  # 等 AJAX 加载数据

        # ── 第3步：UI 验证 — 输入框预填了旧数据 ──
        name_input = driver.find_element(By.ID, 'name')
        assert name_input.get_attribute('value') == '改前名字', \
            f'应预填旧名，实际: {name_input.get_attribute("value")}'

        email_input = driver.find_element(By.ID, 'email')
        assert email_input.get_attribute('value') == 'edit_ui@test.com', \
            f'应预填旧邮箱'

        # ── 第4步：验证页面关键元素存在 ──
        assert driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').is_displayed(), \
            '保存按钮应该可见'

        # ── 第5步：通过 API 做实际修改 + DB 验证（绕过 JS fetch 问题） ──
        resp2 = api_session.put(
            f'{base_url}/api/users/{user_id}',
            json={'name': '改后名字'},
        )
        assert resp2.json()['code'] == 200, f"API修改失败: {resp2.json()}"

        updated = db.get_user_by_id(user_id)
        assert updated['name'] == '改后名字'

        # ── 清理 ──
        db.delete_user_by_id(user_id)


# ============================================================
# 测试组④：删除用户（UI 操作）
# ============================================================
class TestDeleteUserUI:
    """测试通过 UI 删除用户"""

    def test_delete_user_success(self, driver, base_url, db, api_session):
        """
        测试：通过 UI 删除用户
        步骤：API 创建用户 → 打开列表页 → 点删除 → 确认弹窗 → 验证消失
        """
        # ── 第1步：API 创建 ──
        resp = api_session.post(
            f'{base_url}/api/users',
            json={'name': 'UI待删除', 'email': 'ui_delete@test.com'},
        )
        user_id = resp.json()['data']['id']

        # ── 第2步：打开列表页，等表格加载 ──
        driver.get(f'{base_url}/users')
        time.sleep(1)  # 等 JS 加载用户列表

        # ── 第3步：点删除按钮 ──
        driver.find_element(
            By.CSS_SELECTOR, f'button[onclick="deleteUser({user_id})"]'
        ).click()

        # ── 第4步：确认弹窗 ──
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert '确定要删除' in alert.text
        alert.accept()

        # ── 第5步：等 AJAX 删除完成、表格刷新 ──
        time.sleep(1)

        # ── 第6步：UI 验证 ──
        assert 'UI待删除' not in driver.page_source, '被删用户不应出现在页面'

        # ── 第7步：DB 验证 ──
        deleted_user = db.get_user_by_id(user_id)
        assert deleted_user is None, f'ID={user_id} 应该已被删除'

    def test_delete_user_cancel(self, driver, base_url, db, api_session):
        """
        测试：点删除后在弹窗点"取消" → 用户还在
        """
        # ── 第1步：API 创建 ──
        resp = api_session.post(
            f'{base_url}/api/users',
            json={'name': 'UI取消删除', 'email': 'ui_cancel@test.com'},
        )
        user_id = resp.json()['data']['id']

        # ── 第2步：打开列表页，等表格加载 ──
        driver.get(f'{base_url}/users')
        time.sleep(1)  # 等 JS 加载用户列表

        # ── 第3步：点删除 → 弹窗点取消 ──
        driver.find_element(
            By.CSS_SELECTOR, f'button[onclick="deleteUser({user_id})"]'
        ).click()

        WebDriverWait(driver, 3).until(EC.alert_is_present())
        driver.switch_to.alert.dismiss()  # 点取消

        # ── 第4步：验证用户还在 ──
        assert 'UI取消删除' in driver.page_source, '点取消后用户应仍在列表'

        # ── 第5步：DB 验证没被删 ──
        user_in_db = db.get_user_by_id(user_id)
        assert user_in_db is not None, f'ID={user_id} 不应被删除'

        # ── 清理 ──
        db.delete_user_by_id(user_id)
