"""
用户管理页面对象（Page Object 模式）
==================================
每个类对应一个页面，封装该页面的：
  - 元素定位方式（集中管理，前端改了 id 只改这里）
  - 可执行的操作（填表单、点按钮）
  - 可查询的状态（是否显示、获取文字）

面试可以说：
  把页面元素定位和页面操作封装成类，
  测试用例只调 page 的方法，不直接写 find_element。
  换个前端框架只需要改 Page Object 层，测试用例不受影响。
"""
from selenium.webdriver.common.by import By
from tests.ui.pages.base_page import BasePage


class UserListPage(BasePage):
    """用户列表页 — /users"""

    # ── 元素定位（集中管理，一个地方改） ──
    BTN_ADD = (By.LINK_TEXT, '新增用户')
    # By.LINK_TEXT = 按超链接的完整文字来找元素
    TABLE = (By.ID, 'userTable')
    TABLE_BODY = (By.ID, 'userTableBody')
    EMPTY_HINT = (By.ID, 'emptyHint')

    def open(self, base_url):
        """打开用户列表页"""
        self.driver.get(f'{base_url}/users')

    def click_add_button(self):
        """点"新增用户"按钮 → 跳转到新增页面"""
        self.click(*self.BTN_ADD)
        # *元组 = 拆包，等价于 self.click(By.LINK_TEXT, '新增用户')

    def get_table_text(self):
        """获取表格内容（用于验证用户是否出现在列表里）"""
        return self.get_text(*self.TABLE)

    def is_empty_hint_displayed(self):
        """判断"暂无数据"是否可见"""
        return self.is_displayed(*self.EMPTY_HINT)

    def click_edit_button(self, user_id):
        """点指定用户的编辑按钮（通过 href 属性定位）"""
        self.click(By.CSS_SELECTOR, f'a[href="/users/{user_id}/edit"]')

    def click_delete_button(self, user_id):
        """点指定用户的删除按钮（通过 onclick 属性定位）"""
        self.click(By.CSS_SELECTOR, f'button[onclick="deleteUser({user_id})"]')


class CreateUserPage(BasePage):
    """新增用户页 — /users/create"""

    # ── 元素定位 ──
    INPUT_NAME = (By.ID, 'name')
    INPUT_EMAIL = (By.ID, 'email')
    INPUT_PHONE = (By.ID, 'phone')
    BTN_SUBMIT = (By.CSS_SELECTOR, 'button[type="submit"]')
    ERROR_MSG = (By.ID, 'message')

    def open(self, base_url):
        """打开新增用户页面"""
        self.driver.get(f'{base_url}/users/create')

    def fill_name(self, text):
        """在姓名输入框输入文字"""
        self.type(*self.INPUT_NAME, text)

    def fill_email(self, text):
        """在邮箱输入框输入文字"""
        self.type(*self.INPUT_EMAIL, text)

    def fill_phone(self, text):
        """在手机号输入框输入文字"""
        self.type(*self.INPUT_PHONE, text)

    def fill_form(self, name, email, phone=None):
        """一次性填完整张表单（三步合一）"""
        self.fill_name(name)
        self.fill_email(email)
        if phone:
            self.fill_phone(phone)

    def click_submit(self):
        """点提交按钮"""
        self.click(*self.BTN_SUBMIT)

    def get_error_message(self):
        """获取错误提示文字（用于断言校验失败时的提示内容）"""
        return self.get_text(*self.ERROR_MSG)


class EditUserPage(BasePage):
    """编辑用户页 — /users/<id>/edit"""

    # ── 元素定位（跟新增页一样的表单结构） ──
    INPUT_NAME = (By.ID, 'name')
    INPUT_EMAIL = (By.ID, 'email')
    INPUT_PHONE = (By.ID, 'phone')
    BTN_SUBMIT = (By.CSS_SELECTOR, 'button[type="submit"]')
    ERROR_MSG = (By.ID, 'message')

    def open(self, base_url, user_id):
        """打开编辑页面，需要传用户 ID"""
        self.driver.get(f'{base_url}/users/{user_id}/edit')

    def get_name_value(self):
        """获取输入框当前值（验证页面加载时预填了旧数据）"""
        el = self.find(*self.INPUT_NAME)
        return el.get_attribute('value')

    def clear_and_fill_name(self, text):
        """清空旧名 → 填新名"""
        self.type(*self.INPUT_NAME, text)

    def click_submit(self):
        """点保存修改按钮"""
        self.click(*self.BTN_SUBMIT)

    def get_error_message(self):
        return self.get_text(*self.ERROR_MSG)
