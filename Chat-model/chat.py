from langchain_core import chat_history
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

chatHistory = []

while True:

    user_prompt = input("You : ")
    chatHistory.append(user_prompt)
    response = model.invoke(chatHistory)
    chatHistory.append(response.content)
    print("AI : ",response.content)

