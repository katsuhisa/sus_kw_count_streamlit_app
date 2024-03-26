# services/text_extraction.py
from pdfminer.high_level import extract_text
import requests
from bs4 import BeautifulSoup

def extract_text_from_pdf(uploaded_file):
    return extract_text(uploaded_file)

def extract_text_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.get_text()
