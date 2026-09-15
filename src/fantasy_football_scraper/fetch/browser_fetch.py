import asyncio
from itertools import chain

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


def fetch_player_rating(driver):
    driver.implicitly_wait(0.5)
    driver.find_element(By.ID, "disagree-btn").click()
    player_info = []
    for team_selector in [".team-home", ".team-away"]:
        driver.implicitly_wait(0.5)
        team_button = driver.find_elements(By.CSS_SELECTOR, team_selector)[-1]
        team_button.click()
        team_player_info = driver.find_elements(By.CSS_SELECTOR, ".player-info")
        player_info.append(
            [
                rating.get_attribute("innerHTML")
                for rating in team_player_info
                if rating.is_displayed()
            ]
        )
    return list(chain.from_iterable(player_info))


def browser_extraction(driver_path: str, url: str):
    try:
        driver = create_driver(driver_path=driver_path)
        driver.get(url=url)
        html_page = driver.page_source
        player_rating = fetch_player_rating(driver=driver)
        return html_page, player_rating
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
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Venezia-Fiorentina/17994/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Genoa-Frosinone/17987/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Lazio-Milan/17989/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Atalanta-Cagliari/17985/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Lecce-Monza/17990/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Napoli-Bologna/17991/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Sassuolo-Juventus/17992/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Como-Parma/17986/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Torino-Roma/17993/pagelle",
        "https://www.fantacalcio.it/serie-a/calendario/4/2026-2027/Inter-Udinese/17988/pagelle",
    ]

    res = asyncio.run(async_browsers(urls=urls, driver_path=driver_path))
    print(res)
