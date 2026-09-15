import asyncio
from itertools import chain

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.selenium_manager import SeleniumManager

from fantasy_football_scraper import config


def resolve_driver_path() -> str:
    paths = SeleniumManager().binary_paths(["--browser", "chrome"])
    return paths["driver_path"]


def create_driver(driver_path: str):
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    return webdriver.Chrome(
        service=service,
        options=options,
    )


def extract_parsed_html(driver) -> str:
    driver.find_element(By.ID, "disagree-btn").click()

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
    semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_BROWSERS)

    async def run(url):
        async with semaphore:
            return await asyncio.to_thread(browser_extraction, driver_path, url)

    return await asyncio.gather(*(run(url) for url in urls))


if __name__ == "__main__":
    driver_path = resolve_driver_path()
    urls = [
        "https://www.fantacalcio.it/serie-a/calendario/3/2026-27/inter-napoli/17980/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Genoa-Frosinone/17987/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Lazio-Milan/17989/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Atalanta-Cagliari/17985/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Lecce-Monza/17990/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Napoli-Bologna/17991/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Sassuolo-Juventus/17992/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Como-Parma/17986/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Torino-Roma/17993/pagelle",
        # "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Inter-Udinese/17988/pagelle",
    ]

    res = asyncio.run(async_browsers(urls=urls, driver_path=driver_path))
    with open('data/ratings_5.html', 'w') as file:
        file.write(res[0])
