from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Locate file relative to this script
file_path = Path(__file__).parent / "stock_knowlage.txt"
docs = TextLoader(str(file_path), encoding="utf-8").load()

temp = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a AI that Summarizes the text"),
        ("human", "{data}")
    ]
)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

prompt = temp.format_messages(data=docs[0].page_content)

result = model.invoke(prompt)

print(result.content)
