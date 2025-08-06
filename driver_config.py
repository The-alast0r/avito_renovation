import os
import json
import random
import free_proxy_parser
from fake_useragent import UserAgent
from fake_useragent import FakeUserAgentError
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType

PROXY = 'http://user314205:sjxncy@45.145.3.130:8492'

# Конфигурация драйвера
class DriverConfiguration:
    def __init__(self):

        # Options
        try:
            ua = UserAgent().getFirefox
        except FakeUserAgentError:
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        self.options = Options()
        self.options.add_argument(f'--user-agent={ua}')
        # self.options.add_argument('--headless=new')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument('--disable-webrtc')
        self.options.add_argument('--ignore-certificate-errors')

        # Free-proxy
        # proxy_list    = free_proxy_parser.parse_proxy()
        # proxy_address = proxy_list[random.randint(0, len(proxy_list) - 1)]

        # self.proxy = {
        #     'proxy': {
        #         'http': f'http://{proxy_address}',
        #         'https': f'http://{proxy_address}'
        #     }
        # }
        # self.options.add_argument(f'--proxy-server=http://{proxy_address}')
        # self.proxy = {}
        # Service
        self.service = Service(GeckoDriverManager().install())

    
    def get_options(self):
        return self.options

    def get_service(self):
        return self.service

    def get_proxy(self):
        return self.proxy







    #TODO: Модификация для прокси с аутентификацией
    def create_firefox_proxy_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
        
        # Директория для расширения
        ext_dir = os.path.join(os.getcwd(), "firefox_proxy_ext")
        os.makedirs(ext_dir, exist_ok=True)

        # Manifest.json
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth Helper",
            "version": "1.0",
            "description": "Handles proxy authentication",
            "permissions": [
                "proxy",
                "webRequest",
                "webRequestBlocking",
                "<all_urls>"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }
        
        with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)

        # Background.js
        background_js = f"""
        // Настройка прокси
        var config = {{
            mode: "fixed_servers",
            rules: {{
                proxyForHttp: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: {proxy_port}
                }},
                proxyForHttps: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: {proxy_port}
                }},
                proxyForFtp: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: {proxy_port}
                }}
            }}
        }};

        // Применяем настройки прокси
        browser.proxy.settings.set({{value: config}});

        // Обработчик аутентификации
        browser.webRequest.onAuthRequired.addListener(
            function(details) {{
                return {{
                    authCredentials: {{
                        username: "{proxy_user}",
                        password: "{proxy_pass}"
                    }}
                }};
            }},
            {{urls: ["<all_urls>"]}},
            ["blocking"]
        );

        console.log("Proxy extension loaded");
        """
        
        with open(os.path.join(ext_dir, "background.js"), "w") as f:
            f.write(background_js)
        
        return ext_dir