"""
我的第一条 Selenium 测试
========================
目标：用代码打开浏览器，访问用户列表页，验证页面标题
"""
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.open_browser
def test_open_browser():
    # 第1步：设置浏览器选项
    options = Options()
    options.add_argument('--window-size=800,600')
    # 第2步：启动浏览器
    driver = webdriver.Edge(options=options)
    driver.get('http://127.0.0.1:5000/users')
    time.sleep(2)
    page_title = driver.title  # 从浏览器那里拿当前页面的标题
    print('页面标题是：', page_title)  # 打印到终端，让你能看到
    assert '用户管理系统' in page_title  # 断言：标题里必须包含"用户管理系统"
    driver.quit()

@pytest.mark.fill_form
def test_fill_form():
    """测试：能打开新增页，找到输入框，填文字"""
    # 第1步：启动浏览器
    options = Options()
    options.add_argument('--window-size=800,600')
    driver = webdriver.Edge(options=options)
    driver.implicitly_wait(10)

    # 第2步：打开新增用户页面
    driver.get('http://127.0.0.1:5000/users/create')


    # 第3步：找到"姓名"输入框，填文字
    name_input = driver.find_element(By.ID, 'name')
    name_input.send_keys('张三')
    #  ↑ send_keys = 模拟键盘敲字，一个字一个字敲进去

    # 第4步：找到"邮箱"输入框，填文字
    email_input = driver.find_element(By.ID, 'email')
    email_input.send_keys(f'test{int(time.time())}@test.com')
    # ↑ int(time.time()) = 当前时间戳，每次运行不一样，邮箱不会重复

    # 第5步：点击提交按钮（用按钮文字定位，比数 div 更可靠）
    driver.find_element(By.XPATH, "//button[text()='提交']").click()
    wait = WebDriverWait(driver, 10)
    alert = wait.until(EC.alert_is_present())
    print('弹窗文字：', alert.text)
    alert.accept()

    # 点"确定"关掉弹窗

    # 第7步：alert 关闭后 JS 会跳转到 /users 列表页，等一下页面加载
    time.sleep(2)

    # 第6步：关浏览器
    driver.quit()


