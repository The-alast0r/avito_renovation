from fake_useragent import UserAgent
from fake_useragent import FakeUserAgentError
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Конфигурация драйвера
class DriverConfiguration:
    """Класс конфигурации драйвера."""

    def __init__(self):

        # Options
        try:
            ua = UserAgent().getFirefox
        except FakeUserAgentError:
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        self.options = Options()
        self.options.add_argument(f'--user-agent={ua}')
        self.options.add_argument('--headless=new')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument('--disable-webrtc')
        self.options.add_argument('--ignore-certificate-errors')

        # Service
        self.service = Service(GeckoDriverManager().install())

    def get_options(self):
        return self.options

    def get_service(self):
        return self.service