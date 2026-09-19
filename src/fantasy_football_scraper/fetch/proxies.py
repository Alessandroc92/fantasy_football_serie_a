import os
import random
from dotenv import load_dotenv
import niquests

load_dotenv()

PROXY_PROVIDER = os.getenv("PROXY_PROVIDER")
PROXY_API_KEY = os.getenv("PROXY_API_KEY")


def generate_proxy() -> str:
    url = f"https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25"
    r = niquests.get(
        url=url,
        headers={
            "Authorization": f"Token {PROXY_API_KEY}",
        },
    )
    proxy_results = random.choice(r.json()["results"])
    return f"{proxy_results.get("proxy_address")}:{proxy_results.get("port")}"


if __name__ == "__main__":
    x = generate_proxy_dict()
    print(x)
    
