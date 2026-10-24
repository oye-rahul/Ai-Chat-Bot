from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

data = PyPDFLoader("rag_test_knowledge_base.pdf")

docs = data.load()


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "]
)

chunks = splitter.split_documents(docs)

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
