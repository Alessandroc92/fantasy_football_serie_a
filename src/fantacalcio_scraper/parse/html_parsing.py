from bs4 import BeautifulSoup


def extract_match_urls(html: str | None = None): 
    bs = BeautifulSoup(html, 'html.parser')
    options = bs.select('select#matchControl option')
    return [option.get('value') for option in options if option.get('value')]

if __name__ == '__main__':
    print(extract_matchday_urls())