import sys
import os
import requests
from bs4 import BeautifulSoup
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus.tables import TableStyle
from reportlab.lib.units import inch

# Add the project root to sys.path for proper imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scraper.utils import clean_text

def scrape_enhanced_wikipedia(topic=None):
    # Get the topic from the user if not provided
    if not topic:
        topic = input("Enter a topic to scrape from Wikipedia: ")
    
    # Wikipedia URL
    url = f'https://en.wikipedia.org/wiki/{topic}'
    
    try:
        # Send a request to the Wikipedia page
        response = requests.get(url)
        
        # Check if the page was fetched successfully
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get the page title
            title = soup.find('h1', {'id': 'firstHeading'}).text
            
            # Find the main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            
            # Extract all sections with headings
            sections = []
            current_heading = None
            current_content = []
            
            # Get the main content area
            main_content = content_div.find('div', {'class': 'mw-parser-output'})
            if not main_content:
                main_content = content_div
            
            # Process all elements in the main content - improved to capture all sections
            for element in main_content.children:
                if element.name in ['h2', 'h3', 'h4']:
                    # Save previous section if exists
                    if current_heading and current_content:
                        sections.append({
                            'heading': current_heading,
                            'level': int(current_heading[0][1]),  # h2 -> 2, h3 -> 3, etc.
                            'content': '\n\n'.join(current_content)
                        })
                    
                    # Start new section
                    heading_text = element.get_text().replace('[edit]', '').strip()
                    current_heading = (element.name, heading_text)
                    current_content = []
                elif element.name == 'p' and element.text.strip():
                    if current_heading:
                        current_content.append(clean_text(element.text))
                    else:
                        # This is intro paragraph before any heading
                        if not sections:
                            sections.append({
                                'heading': ('h1', 'Introduction'),
                                'level': 1,
                                'content': clean_text(element.text)
                            })
                        else:
                            # Append to introduction
                            sections[0]['content'] += '\n\n' + clean_text(element.text)
                # Also capture lists and tables within sections
                elif element.name in ['ul', 'ol', 'table'] and current_heading:
                    list_content = clean_text(element.get_text().strip())
                    if list_content:
                        current_content.append(list_content)
            
            # Add the last section if exists
            if current_heading and current_content:
                sections.append({
                    'heading': current_heading,
                    'level': int(current_heading[0][1]),
                    'content': '\n\n'.join(current_content)
                })
                
            # Also check for any sections that might be in divs (sometimes Wikipedia uses this structure)
            for div in main_content.find_all('div', {'class': 'mw-heading'}):
                heading_element = div.find(['h2', 'h3', 'h4'])
                if heading_element:
                    heading_text = heading_element.get_text().replace('[edit]', '').strip()
                    heading_level = int(heading_element.name[1])
                    content_elements = []
                    
                    # Get all paragraph siblings until next heading
                    for sibling in div.find_next_siblings():
                        if sibling.name in ['h2', 'h3', 'h4'] or sibling.find(['h2', 'h3', 'h4']):
                            break
                        if sibling.name == 'p' and sibling.text.strip():
                            content_elements.append(clean_text(sibling.text))
                    
                    if content_elements:
                        sections.append({
                            'heading': (heading_element.name, heading_text),
                            'level': heading_level,
                            'content': '\n\n'.join(content_elements)
                        })
            
            # Extract references with URLs
            references = []
            ref_urls = []
            ref_section = soup.find('div', {'class': 'reflist'})
            if ref_section:
                for ref in ref_section.find_all('li'):
                    ref_text = ref.get_text()
                    references.append(ref_text)
                    
                    # Try to extract URLs from references
                    ref_link = ref.find('a', {'class': 'external'})
                    if ref_link and 'href' in ref_link.attrs:
                        ref_urls.append({'text': ref_text[:50] + '...', 'url': ref_link['href']})
            
            # If no references found in reflist, try to find citations
            if not references:
                citations = content_div.find_all('sup', {'class': 'reference'})
                for citation in citations[:30]:  # Increased limit to 30 citations
                    cite_id = citation.find('a').get('href', '').replace('#', '')
                    if cite_id:
                        cite_note = soup.find('li', {'id': cite_id})
                        if cite_note:
                            ref_text = cite_note.get_text()
                            references.append(ref_text)
                            
                            # Try to extract URL
                            ref_link = cite_note.find('a', {'class': 'external'})
                            if ref_link and 'href' in ref_link.attrs:
                                ref_urls.append({'text': ref_text[:50] + '...', 'url': ref_link['href']})
            
            # Extract images from various sources
            images = []
            
            # Get thumbnail images
            for img in content_div.find_all('img', {'class': 'thumbimage'})[:15]:
                if 'src' in img.attrs:
                    img_src = img['src']
                    if not img_src.startswith('http'):
                        img_src = 'https:' + img_src
                    images.append(img_src)
            
            # Get images from infobox
            infobox = content_div.find('table', {'class': 'infobox'})
            if infobox:
                for img in infobox.find_all('img')[:5]:
                    if 'src' in img.attrs:
                        img_src = img['src']
                        if not img_src.startswith('http'):
                            img_src = 'https:' + img_src
                        if img_src not in images:  # Avoid duplicates
                            images.append(img_src)
            
            # Get images from the main content area
            for img in content_div.find_all('img')[:20]:
                if 'src' in img.attrs and img.get('width') and int(img.get('width', 0)) > 100:
                    img_src = img['src']
                    if not img_src.startswith('http'):
                        img_src = 'https:' + img_src
                    if img_src not in images:  # Avoid duplicates
                        images.append(img_src)
            
            # Generate enhanced PDF with table of contents
            generate_enhanced_pdf(topic, title, sections, references, images, url, ref_urls)
            
            # Generate summarized CSV
            generate_summarized_csv(topic, title, sections, url)
            
            print(f"\nEnhanced PDF for {title} has been generated successfully!")
            print(f"File saved as: {topic}_enhanced_wikipedia.pdf")
            print(f"Summarized CSV saved as: {topic}_wikipedia_summary.csv")
            
            return {
                'title': title,
                'sections': sections,
                'references': references,
                'images': images,
                'url': url
            }
        else:
            print(f"Error: Unable to fetch page for {topic}. HTTP Status Code: {response.status_code}")
            return {'error': f'Failed to fetch page: {response.status_code}'}
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {'error': str(e)}

def generate_enhanced_pdf(topic, title, sections, references, images, url, ref_urls=None):
    pdf_file = f'{topic}_enhanced_wikipedia.pdf'
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=20, bottomMargin=20, leftMargin=30, rightMargin=30)
    styles = getSampleStyleSheet()
    
    # Create enhanced custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=12,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.darkblue,
        borderWidth=0,
        borderPadding=5,
        borderColor=colors.lightgrey,
        borderRadius=2
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    h3_style = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,  # Line spacing
        spaceAfter=8
    )
    
    url_style = ParagraphStyle(
        'URL',
        parent=normal_style,
        textColor=colors.blue,
        fontSize=9
    )
    
    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.darkgrey,
        alignment=1  # Center alignment
    )
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        spaceBefore=6
    )
    
    # Create the PDF content
    elements = []
    
    # Add title with better styling
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 15))
    
    # Add URL with better styling
    elements.append(Paragraph(f"<b>Source URL:</b> <a href='{url}' color='blue'>{url}</a>", url_style))
    elements.append(Spacer(1, 20))
    
    # Create and add Table of Contents
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name='TOC1', fontSize=14, leading=16, leftIndent=20, textColor=colors.darkblue),
        ParagraphStyle(name='TOC2', fontSize=12, leading=14, leftIndent=40),
        ParagraphStyle(name='TOC3', fontSize=10, leading=12, leftIndent=60)
    ]
    
    # Add TOC header
    elements.append(Paragraph("<b>Table of Contents</b>", h1_style))
    elements.append(Spacer(1, 10))
    elements.append(toc)
    elements.append(Spacer(1, 30))
    
    # Add content sections with proper headings for TOC
    for section in sections:
        heading_level = section['level']
        heading_text = section['heading'][1]
        content_text = section['content']
        
        # Select appropriate heading style based on level
        if heading_level == 1:
            heading_style = h1_style
            bookmark_name = f"h1-{heading_text.lower().replace(' ', '-')}"
        elif heading_level == 2:
            heading_style = h2_style
            bookmark_name = f"h2-{heading_text.lower().replace(' ', '-')}"
        else:  # level 3 or higher
            heading_style = h3_style
            bookmark_name = f"h3-{heading_text.lower().replace(' ', '-')}"
        
        # Add heading with bookmark for TOC
        heading_para = Paragraph(f"<a name='{bookmark_name}'/>{heading_text}", heading_style)
        elements.append(heading_para)
        elements.append(Spacer(1, 8))
        
        # Add content paragraphs
        for paragraph in content_text.split('\n\n'):
            if paragraph.strip():
                elements.append(Paragraph(paragraph, normal_style))
                elements.append(Spacer(1, 8))
    
    # Add images section
    if images:
        elements.append(Paragraph("<b>Images</b>", h1_style))
        elements.append(Spacer(1, 10))
        
        # Process images in pairs when possible
        i = 0
        while i < len(images):
            try:
                # First image in the pair
                img1_url = images[i]
                img1_response = requests.get(img1_url)
                
                if img1_response.status_code == 200:
                    img1 = Image.open(io.BytesIO(img1_response.content))
                    
                    # Check if we have a second image to pair
                    if i + 1 < len(images):
                        # Try to get second image
                        img2_url = images[i + 1]
                        img2_response = requests.get(img2_url)
                        
                        if img2_response.status_code == 200:
                            # We have two images to display side by side
                            img2 = Image.open(io.BytesIO(img2_response.content))
                            
                            # Calculate sizes for side-by-side display
                            max_width = 250  # Max width for each image when side by side
                            
                            # Resize first image
                            width1, height1 = img1.size
                            if width1 > max_width:
                                ratio = max_width / width1
                                new_width1 = max_width
                                new_height1 = int(height1 * ratio)
                                img1 = img1.resize((new_width1, new_height1))
                            else:
                                new_width1, new_height1 = width1, height1
                                
                            # Resize second image
                            width2, height2 = img2.size
                            if width2 > max_width:
                                ratio = max_width / width2
                                new_width2 = max_width
                                new_height2 = int(height2 * ratio)
                                img2 = img2.resize((new_width2, new_height2))
                            else:
                                new_width2, new_height2 = width2, height2
                            
                            # Save images to memory - convert RGBA to RGB if needed
                            img1_byte_arr = io.BytesIO()
                            if img1.mode == 'RGBA':
                                rgb_img1 = Image.new('RGB', img1.size, (255, 255, 255))
                                rgb_img1.paste(img1, mask=img1.split()[3])  # Use alpha channel as mask
                                rgb_img1.save(img1_byte_arr, format='JPEG')
                            else:
                                img1.save(img1_byte_arr, format=img1.format or 'JPEG')
                            img1_byte_arr.seek(0)
                            
                            img2_byte_arr = io.BytesIO()
                            if img2.mode == 'RGBA':
                                rgb_img2 = Image.new('RGB', img2.size, (255, 255, 255))
                                rgb_img2.paste(img2, mask=img2.split()[3])  # Use alpha channel as mask
                                rgb_img2.save(img2_byte_arr, format='JPEG')
                            else:
                                img2.save(img2_byte_arr, format=img2.format or 'JPEG')
                            img2_byte_arr.seek(0)
                            
                            # Create image objects for PDF
                            img1_for_pdf = RLImage(img1_byte_arr, width=new_width1, height=new_height1)
                            img2_for_pdf = RLImage(img2_byte_arr, width=new_width2, height=new_height2)
                            
                            # Create a table to hold the images side by side
                            image_table = [[img1_for_pdf, img2_for_pdf]]
                            t = Table(image_table, colWidths=[260, 260])
                            t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                  ('LEFTPADDING', (0, 0), (-1, -1), 5),
                                                  ('RIGHTPADDING', (0, 0), (-1, -1), 5)]))
                            elements.append(t)
                            elements.append(Spacer(1, 6))
                            
                            # Add captions in a table too
                            caption_table = [[Paragraph(f"<i>Image source: {img1_url}</i>", caption_style),
                                             Paragraph(f"<i>Image source: {img2_url}</i>", caption_style)]]
                            c = Table(caption_table, colWidths=[260, 260])
                            c.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                  ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                                  ('LEFTPADDING', (0, 0), (-1, -1), 5),
                                                  ('RIGHTPADDING', (0, 0), (-1, -1), 5)]))
                            elements.append(c)
                            elements.append(Spacer(1, 15))
                            
                            # Increment by 2 since we processed two images
                            i += 2
                            continue
                    
                    # If we're here, we're processing a single image
                    # Resize image if needed
                    width, height = img1.size
                    max_width = 450  # Max width for single image
                    if width > max_width:
                        ratio = max_width / width
                        new_width = max_width
                        new_height = int(height * ratio)
                        img1 = img1.resize((new_width, new_height))
                    else:
                        new_width, new_height = width, height
                    
                    # Save image to memory - convert RGBA to RGB if needed
                    img1_byte_arr = io.BytesIO()
                    if img1.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img1.size, (255, 255, 255))
                        rgb_img.paste(img1, mask=img1.split()[3])  # Use alpha channel as mask
                        rgb_img.save(img1_byte_arr, format='JPEG')
                    else:
                        img1.save(img1_byte_arr, format=img1.format or 'JPEG')
                    img1_byte_arr.seek(0)
                    
                    # Add image to PDF
                    img_for_pdf = RLImage(img1_byte_arr, width=new_width, height=new_height)
                    elements.append(img_for_pdf)
                    elements.append(Spacer(1, 6))
                    elements.append(Paragraph(f"<i>Image source: {img1_url}</i>", caption_style))
                    elements.append(Spacer(1, 15))
                    
                    # Increment by 1 since we processed one image
                    i += 1
            except Exception as e:
                print(f"Error processing image {images[i]}: {e}")
                i += 1  # Move to next image even if there's an error
    
    # Add references with URLs when available
    if references:
        elements.append(Paragraph("<b>References</b>", h1_style))
        elements.append(Spacer(1, 10))
        
        # If we have extracted URLs, display them with hyperlinks
        if ref_urls:
            for i, ref_url in enumerate(ref_urls, 1):
                elements.append(Paragraph(
                    f"{i}. {ref_url['text']} <a href='{ref_url['url']}' color='blue'>[Link]</a>", 
                    normal_style
                ))
                elements.append(Spacer(1, 5))
        else:
            # Otherwise just display the references as text
            for i, ref in enumerate(references, 1):
                elements.append(Paragraph(f"{i}. {ref}", normal_style))
                elements.append(Spacer(1, 5))
    
    # Build the PDF
    doc.build(elements)
    print(f"Enhanced PDF with table of contents saved to '{pdf_file}'")

def generate_summarized_csv(topic, title, sections, url):
    import csv
    
    # Create CSV file name
    csv_file = f'{topic}_wikipedia_summary.csv'
    
    # Prepare data for CSV
    # For the summarized version, we'll include:
    # 1. Title and URL
    # 2. Introduction (first section)
    # 3. Section headings with brief summaries
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header
        writer.writerow(["Topic", "Content"])
        
        # Write title and introduction
        intro_content = ""
        if sections and sections[0]['heading'][1] == 'Introduction':
            intro_content = sections[0]['content']
            # Limit to first paragraph for summary
            if '\n\n' in intro_content:
                intro_content = intro_content.split('\n\n')[0]
        
        # Create a summary that includes the title, URL, and introduction
        summary = f"Title: {title}\n\nURL: {url}\n\n{intro_content}\n\nSections:\n"
        
        # Add section headings to the summary
        for section in sections:
            if section['heading'][1] != 'Introduction':
                level = section['level']
                heading = section['heading'][1]
                indent = '  ' * (level - 1)
                summary += f"{indent}- {heading}\n"
                
                # Add a brief excerpt from each section (first sentence or limited characters)
                content = section['content']
                if content:
                    first_sentence = content.split('.')[0] + '.'
                    if len(first_sentence) > 100:
                        first_sentence = first_sentence[:97] + '...'
                    summary += f"{indent}  {first_sentence}\n"
        
        # Write the summary to CSV
        writer.writerow([topic, summary])
    
    print(f"Summarized CSV saved to '{csv_file}'")

# Main execution
if __name__ == "__main__":
    scrape_enhanced_wikipedia()