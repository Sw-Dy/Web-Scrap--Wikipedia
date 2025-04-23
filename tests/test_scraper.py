from scraper.wikipedia_scraper import scrape_wikipedia_page
from scraper.wikipedia_api import get_wikipedia_summary

def test_scraper():
    result = scrape_wikipedia_page("https://en.wikipedia.org/wiki/Web_scraping")
    assert 'title' in result
    assert 'content' in result

def test_api():
    result = get_wikipedia_summary("Web scraping")
    assert 'title' in result
    assert 'summary' in result
