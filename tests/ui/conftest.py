"""
UI 测试夹具（fixtures）配置
==========================
conftest.py 是 pytest 特殊文件，自动被加载。
这里管理 Selenium WebDriver 的生命周期（Edge 浏览器启动/关闭）。

面试可以说：
  用 conftest.py 统一管理 WebDriver，
  session 级别复用浏览器窗口提高速度，
  用 pytest_addoption 注册 --headless 参数支持 CI/CD 后台运行。
"""
import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions


def pytest_addoption(parser):
    """给 pytest 添加自定义命令行参数"""
    parser.addoption(
        '--headless',
        action='store_true',
        default=False,
        help='无头模式运行（不弹出浏览器窗口，适合 CI/CD）'
    )


@pytest.fixture(scope='session')
def driver(request):
    """
    WebDriver fixture — session 级别，整个测试只启动一次浏览器
    -------------------------------------------------------------
    为什么 session 而不是 function？
      function 级别每个用例都重启浏览器（每次 2-3 秒），太慢
      session 级别所有用例共用一个浏览器窗口，用例之间互不干扰

    注意：用例里不要调 driver.quit()！这个 fixture 会在全部测试结束时自动 quit
    """
    # 读取 --headless 命令行参数
    headless = request.config.getoption('--headless')

    # 配置 Edge 选项（Edge 跟 Chrome 同一个内核，选项完全兼容）
    options = EdgeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    # 创建 Edge WebDriver
    # Selenium 4.x 会自动查找并使用系统自带的 Edge 驱动
    browser = webdriver.Edge(options=options)
    browser.implicitly_wait(5)

    yield browser
    browser.quit()
