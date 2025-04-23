# Wikipedia Web Scraper

## Overview

This project is a Python-based web scraper that allows users to fetch and save the summary content of a Wikipedia page. The user enters a topic, and the scraper retrieves the corresponding Wikipedia page's introductory content and saves it to a text file.

Watch the demo video to see the scraper in action: [Demo Video](https://1drv.ms/v/c/8c8713fbccf62dfa/EfR3IGmduelHmC_RIoY03WkBlvb8MSBrsia9L4X9mQ7GRw?e=bI6pQD)

## Features

- **User Input**: Enter the topic of interest directly in the console.
- **Dynamic File Saving**: Saves the fetched content in a `.txt` file with the topic name.
- **Error Handling**: Handles errors like missing Wikipedia pages or network issues.
- **Lightweight Dependencies**: Uses Python's `requests` and `BeautifulSoup` libraries for simplicity.

## Installation

1. **Prerequisites**:

   - Python 3.6 or higher installed on your system.
   - Basic understanding of Python and web scraping concepts (optional).

2. **Install Dependencies**: Run the following command to install the required libraries:

   ```bash
   pip install requests beautifulsoup4
   ```

3. **Download the Script**: Save the Python script (`main.py`) in a directory of your choice.

## Usage

1. Open a terminal or command prompt.
2. Navigate to the directory where the script is saved.
3. Run the script using the following command:
   ```bash
   python main.py
   ```
4. Enter the topic you wish to scrape when prompted. For example:
   ```
   Enter a topic to scrape from Wikipedia: Python_(programming_language)
   ```
5. The script will fetch the content and save it to a file named:
   ```
   Python_(programming_language)_wikipedia_content.txt
   ```
   This file will be located in the same directory as the script.

## Example

### Input:

```
Enter a topic to scrape from Wikipedia: Artificial_intelligence
```

### Output File:

**File Name:** `Artificial_intelligence_wikipedia_content.txt`

**Content:**

```
Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans...
```

## How It Works

1. **Input Handling**: The user provides a topic (formatted as it appears in a Wikipedia URL, e.g., `Python_(programming_language)`).
2. **HTTP Request**: The script uses the `requests` library to send a GET request to the Wikipedia page for the topic.
3. **HTML Parsing**: The `BeautifulSoup` library parses the HTML content of the page.
4. **Content Extraction**: The script locates the introductory paragraphs within the page and extracts the text.
5. **File Saving**: The extracted content is written to a `.txt` file named after the topic.
6. **Error Handling**: If the page is not found or if a network error occurs, the script informs the user.

## Code Overview

### Libraries Used

- ``: For sending HTTP requests to Wikipedia.
- ``** (from **``**)**: For parsing and extracting HTML content.

### Key Functions

- ``: Captures the topic from the user.
- ``: Fetches the HTML content of the Wikipedia page.
- ``: Parses the HTML.
- ``: Extracts the paragraph tags containing the introductory content.
- **File Handling**: Writes the extracted content into a `.txt` file.

### Error Handling

- **404 Errors**: If the page does not exist, the script displays "Topic not found on Wikipedia."
- **Network Issues**: The script displays an error message if the request fails due to connectivity issues.

## Known Issues

- The script only fetches the introductory content and does not handle additional sections or sub-sections.
- Does not handle disambiguation pages effectively; the user must specify the correct topic URL.
- Assumes that the Wikipedia page's structure is consistent (may break if Wikipedia changes its HTML structure).

## Future Improvements

- Add support for fetching additional sections of the page.
- Handle disambiguation pages automatically by allowing the user to select the correct topic.
- Include language support for Wikipedia pages in different languages.
- Enhance the user interface with a GUI version.

## COLLABORATORS :
GitHub Username | Role | https://github.com/Adri2204
Adri2204 | Collaborator | Adri2204

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute the code with proper attribution.

## Contributing

If you'd like to contribute, feel free to fork the repository and submit a pull request with your improvements. Suggestions and bug reports are also welcome.

## Contact

For any queries or issues, please reach out to:

- **Name**: Swagnik Dey
- **Email**: Swagnik.dey.official@gmail.com

Happy Scraping!

