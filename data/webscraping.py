import os
import xml.etree.ElementTree as ET
import requests
import json
import base64
import time
from pathlib import Path
import tempfile
from mistralai import Mistral
from mistralai import ImageURLChunk
from pdf2image import convert_from_path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from dotenv import load_dotenv


load_dotenv()


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
PDFS_MARKDOWN_DIR = os.path.join(PROCESSED_DIR, "pdfs_markdown")
MARKDOWN_DIR = os.path.join(PROCESSED_DIR, "website_markdown")
SITEMAP_PATH = os.path.join(RAW_DIR, "sitemap.xml")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(PDFS_MARKDOWN_DIR, exist_ok=True)
os.makedirs(MARKDOWN_DIR, exist_ok=True)

# Function to extract all the URLs from sitemap.xml
def extract_urls_from_sitemap(sitemap_file):
    tree = ET.parse(sitemap_file)
    root = tree.getroot()  # gets the root element of the xml file (<urlset>)
    urls = []
    for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None:
            urls.append(loc.text)
    return urls

# Function to extract PDFs only from the urls
def extract_pdfs_from_urls(urls):
    pdf_urls = []
    for url in urls:
        if url.lower().endswith(".pdf"):
            pdf_urls.append(url)
    return pdf_urls

##############################################
###   Scraping PDF URLs from the website   ###
##############################################

def download_pdf(url, local_path):
    try:
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def process_image_with_mistral(image_path, client):
    try:
        encoded = base64.b64encode(open(image_path, "rb").read()).decode()
        image_response = client.ocr.process(
            document=ImageURLChunk(image_url=f"data:image/png;base64,{encoded}"),
            model="mistral-ocr-latest"
        )
        response_dict = json.loads(image_response.json())
        
        markdown_content = ""
        if "pages" in response_dict and response_dict["pages"]:
            page = response_dict["pages"][0]
            markdown_content = page.get("markdown", "")
            for img in page.get("images", []):
                img_id, img_base64 = img.get("id"), img.get("image_base64")
                if img_id and img_base64:
                    markdown_content = markdown_content.replace(
                        f"![{img_id}]({img_id})", f"![{img_id}]({img_base64})"
                    )
        return markdown_content
    except Exception as e:
        print(f"Failed to process {image_path} with Mistral OCR: {e}")
        return None

def process_pdf_with_mistral(pdf_path, client):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(pdf_path)
            all_markdown = []
            for i, image in enumerate(images):
                image_path = os.path.join(temp_dir, f"page_{i+1}.png")
                image.save(image_path, "PNG")
                page_markdown = process_image_with_mistral(image_path, client)
                if page_markdown:
                    all_markdown.append(page_markdown)
                if i < len(images) - 1:
                    time.sleep(1)
            return "\n\n---\n\n".join(all_markdown)
    except Exception as e:
        print(f"Failed to process PDF {pdf_path}: {e}")
        return None

def process_pdfs(pdf_urls):
    # Initializing Mistral API client
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: Mistral API key not found. Please set it in your .env file.")
        return
    
    client = Mistral(api_key=api_key)
    delay_seconds = 2
    
    for i, pdf_url in enumerate(pdf_urls):
        print(f"Processing PDF {i+1}/{len(pdf_urls)}: {pdf_url}")
        pdf_filename = os.path.basename(pdf_url)
        pdf_name = os.path.splitext(pdf_filename)[0]
        temp_pdf_path = os.path.join(RAW_DIR, pdf_filename)
        markdown_path = os.path.join(PDFS_MARKDOWN_DIR, f"{pdf_name}.md")
        
        if os.path.exists(markdown_path):
            print(f"Markdown file already exists for {pdf_url}, skipping...")
            continue
        
        if download_pdf(pdf_url, temp_pdf_path):
            markdown_content = process_pdf_with_mistral(temp_pdf_path, client)
            if markdown_content:
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"Successfully saved markdown for {pdf_url} to {markdown_path}")
            else:
                print(f"Failed to generate markdown for {pdf_url}")
            os.remove(temp_pdf_path)
        else:
            print(f"Skipping {pdf_url} due to download failure")
        
        if i < len(pdf_urls) - 1:
            print(f"Waiting {delay_seconds} seconds before next request...")
            time.sleep(delay_seconds)

    print("PDF processing completed. Markdowns saved to", PDFS_MARKDOWN_DIR)

##############################################
### Scraping non-PDF URLs from the website ###
##############################################

def html_to_markdown(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error retrieving {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    main_content = soup.find("div", class_="region-content")

    if not main_content:
        main_content = soup.find("main") or soup.find("body")

    if not main_content:
        print(f"Main content not found for {url}")
        return None

    markdown = md(str(main_content))
    return markdown

def scrape_urls_to_markdown(urls, output_dir):
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Scraping {url}")
        markdown = html_to_markdown(url)
        if markdown:
            # Create a clean filename
            filename = f"page_{i+1}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {url}\n\n")
                f.write(markdown)
        time.sleep(1)

def main():
    if not os.path.exists(SITEMAP_PATH):
        print(f"Error: Sitemap not found at {SITEMAP_PATH}")
        return
    
    urls = extract_urls_from_sitemap(SITEMAP_PATH)
    pdf_urls = extract_pdfs_from_urls(urls)
    non_pdf_urls = [url for url in urls if url not in pdf_urls]
    

    process_pdfs(pdf_urls)
    scrape_urls_to_markdown(non_pdf_urls, MARKDOWN_DIR)
    
    print(f"Scraping completed. Data stored in {PROCESSED_DIR}")

if __name__ == "__main__":
    main()