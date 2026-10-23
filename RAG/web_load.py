import os
import sys

# Set User-Agent and UTF-8 output encoding before importing loader
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
sys.stdout.reconfigure(encoding="utf-8")

from langchain_community.document_loaders import WebBaseLoader

url = "https://www.investopedia.com/terms/s/stockmarket.asp"

data = WebBaseLoader(url)

docs = data.load()

print(docs[0].page_content[:1000])
