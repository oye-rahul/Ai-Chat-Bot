from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

file_path = Path(__file__).parent / "rag_test_knowledge_base.pdf"
docs = PyPDFLoader(str(file_path)).load()

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
