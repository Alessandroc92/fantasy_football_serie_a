import asyncio
from itertools import chain
import threading

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from fantasy_football_scraper import config

from concurrent.futures import ThreadPoolExecutor

selenium_executor = ThreadPoolExecutor(
    max_workers=config.MAX_CONCURRENT_BROWSERS,
    thread_name_prefix="selenium"
)


def resolve_driver_path() -> str:
    paths = SeleniumManager().binary_paths(["--browser", "chrome"])
    return paths["driver_path"]


def create_driver(driver_path: str):
    service = Service(driver_path,
    log_output="logs/chromedriver.log",
    service_args=["--verbose"],
    popen_kw={"close_fds": False},
)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    return webdriver.Chrome(
        service=service,
        options=options,
    )


def extract_parsed_html(driver) -> str:
    button = WebDriverWait(
        driver, config.SELENIUM_STANDARD_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "disagree-btn"))
            )
    button.click()

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
    try:
        driver = create_driver(driver_path=driver_path)
        driver.get(url=url)
        return extract_parsed_html(driver=driver)
    finally:
        driver.quit()


async def async_browsers(urls: list[str], driver_path: str):
    loop = asyncio.get_running_loop()

    async def run(url):
        return await loop.run_in_executor(selenium_executor, browser_extraction, driver_path, url)

    return await asyncio.gather(*(run(url) for url in urls))