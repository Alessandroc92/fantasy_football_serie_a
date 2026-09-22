import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import dotenv
from bs4 import BeautifulSoup

dotenv.load_dotenv()
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from fantasy_football_scraper import config
from fantasy_football_scraper.fetch import proxies

PROXY_PROVIDER = os.getenv("PROXY_PROVIDER")
PROXY_PORT = os.getenv("PROXY_PORT")

selenium_executor = ThreadPoolExecutor(
    max_workers=config.MAX_CONCURRENT_BROWSERS, thread_name_prefix="selenium"
)


def resolve_driver_path() -> str:
    paths = SeleniumManager().binary_paths(["--browser", "chrome"])
    return paths["driver_path"]


def create_driver(driver_path: str):
    service = Service(
        driver_path,
        log_output="logs/chromedriver.log",
        service_args=["--verbose"],
        popen_kw={"close_fds": False},
    )

    proxy_string = proxies.generate_proxy()
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = proxy_string
    proxy.ssl_proxy = proxy_string

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.proxy = proxy

    return webdriver.Chrome(
        service=service,
        options=options,
    )


def close_ads(driver):
    try:
        iframe = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'iframe[id*="Smartitial"]')
            )
        )

        driver.switch_to.frame(iframe)

        close_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "VideoSmartitialCloseBtn"))
        )

        close_btn.click()

    finally:
        driver.switch_to.default_content()


def regular_flow(driver):
    for _ in range(config.SELENIUM_BUTTON_ATTEMPTS):
        try:
            button = WebDriverWait(driver, config.SELENIUM_STANDARD_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "accept-btn"))
            )
            button.click()
            break
        except StaleElementReferenceException:
            continue


def alternative_flow(driver):
    button = WebDriverWait(driver, config.SELENIUM_STANDARD_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="CONFIRM"]'))
    )
    button.click()
    button = WebDriverWait(driver, config.SELENIUM_STANDARD_TIMEOUT).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[aria-label="Close success modal"]')
        )
    )
    button.click()


def extract_parsed_html(driver) -> str:
    try:
        regular_flow(driver=driver)
    except TimeoutException:
        alternative_flow(driver=driver)
    except ElementClickInterceptedException:
        close_ads(driver=driver)
        regular_flow(driver=driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    visible_ids = set()

    for selector in (".team-away", ".team-home"):
        button = driver.find_elements(By.CSS_SELECTOR, selector)[-1]
        button.click()

        visible_ids.update(
            article.get_attribute("data-r")
            for article in driver.find_elements(By.CSS_SELECTOR, "article")
            if article.is_displayed()
        )

    for article in soup.select("article"):
        if article.get("data-r") not in visible_ids:
            article.decompose()

    return str(soup)


def browser_extraction(driver_path: str, url: str) -> str:
    driver = create_driver(driver_path=driver_path)

    try:
        driver.get(url)
        html = extract_parsed_html(driver=driver)

    except Exception:
        input("Press ENTER when you're doing inspecting the browser error.")
        driver.quit()
        raise

    else:
        driver.quit()
        return html


async def async_browsers(urls: list[str], driver_path: str):
    loop = asyncio.get_running_loop()

    async def run(url):
        return await loop.run_in_executor(
            selenium_executor, browser_extraction, driver_path, url
        )

    return await asyncio.gather(*(run(url) for url in urls))
