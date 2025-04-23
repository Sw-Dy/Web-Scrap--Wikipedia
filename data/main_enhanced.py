import sys
import os

# Add the project root to sys.path for proper imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from enhanced_wikipedia_scraper import scrape_enhanced_wikipedia

def main():
    print("Enhanced Wikipedia Scraper")
    print("==========================")
    print("This tool scrapes Wikipedia articles and generates comprehensive PDF files")
    print("with table of contents, all sections, images, and references.\n")
    
    # Option to provide topic as command line argument
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        print(f"Scraping topic: {topic}")
        result = scrape_enhanced_wikipedia(topic)
    else:
        # Otherwise prompt the user
        result = scrape_enhanced_wikipedia()
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    print("\nScraping completed successfully!")
    print(f"Title: {result['title']}")
    print(f"Number of sections: {len(result['sections'])}")
    print(f"Number of images: {len(result['images'])}")
    print(f"Number of references: {len(result['references'])}")
    
    # Print section headings
    print("\nSections:")
    for section in result['sections']:
        level = section['level']
        heading = section['heading'][1]
        indent = '  ' * (level - 1)
        print(f"{indent}- {heading}")

if __name__ == "__main__":
    main()