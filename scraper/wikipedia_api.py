import wikipediaapi

def get_wikipedia_summary(title, lang="en"):
    wiki = wikipediaapi.Wikipedia(lang)
    page = wiki.page(title)
    if page.exists():
        return {'title': page.title, 'summary': page.summary[:1000], 'url': page.fullurl}
    else:
        return {'error': 'Page not found'}
