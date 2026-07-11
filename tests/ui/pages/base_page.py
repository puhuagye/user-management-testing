"""
Page Object 基类
================
所有页面对象都继承这个类，把公共操作（等待、点击、输入）封装在这里。

面试可以说：Page Object 模式把页面元素和操作封装成类，
测试用例不直接写 find_element，而是调 page.click_submit()。
换个前端框架只需要改 Page Object 层，测试用例不受影响。
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """所有页面对象的父类，提供通用的页面操作方法"""

    def __init__(self, driver):
        """
        driver = Selenium WebDriver 实例（浏览器驱动器）
        所有页面共享同一个 driver，因为测试是在同一个浏览器窗口里进行的
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=10)
        # ↑ WebDriverWait 是"显式等待"工具，最多等 10 秒
        # 如果元素在 2 秒就出现了，它不会傻等 10 秒，而是立刻返回

    def open(self, url):
        """打开指定 URL"""
        self.driver.get(url)

    def find(self, by, value):
        """
        查找单个元素，带显式等待
        --------------------------
        by = 定位方式（By.ID, By.CSS_SELECTOR 等）
        value = 定位值（如 "name"、"button[type='submit']"）
        
        为什么用显式等待？
          页面可能还没加载完，如果直接 find_element 会报 NoSuchElementException
          显式等待会等元素出现在页面上再返回，最多等 10 秒
        """
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        )

    def find_clickable(self, by, value):
        """
        查找可点击的元素，带显式等待
        跟 find() 的区别：不仅要"出现"，还要"能点"（可见+可用）
        用于按钮、链接等需要点击的元素
        """
        return self.wait.until(
            EC.element_to_be_clickable((by, value))
        )

    def click(self, by, value):
        """等待元素可点击后，点击它"""
        el = self.find_clickable(by, value)
        el.click()

    def type(self, by, value, text):
        """
        在输入框里输入文字
        步骤：清空 → 输入（模拟用户先选中旧文字 → 敲新文字）
        """
        el = self.find(by, value)
        el.clear()        # 先清空（万一输入框里有旧文字）
        el.send_keys(text)  # 输入新文字

    def get_text(self, by, value):
        """获取元素的文字内容（用于断言）"""
        el = self.find(by, value)
        return el.text

    def is_displayed(self, by, value):
        """判断元素是否可见（用于断言某个东西出现了）"""
        try:
            el = self.find(by, value)
            return el.is_displayed()
        except Exception:
            return False
