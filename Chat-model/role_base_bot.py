# role base ai chat bot 
from numpy import choose
from langchain_core import chat_history
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

print("choose the role of your AI")
print("1. Angey")
print("2. Very Funny")

role = input("Enter your choice: ")

if role == "1":
    role = "You are very angey and always be angry"
elif role == "2":
    role = "You are very funny and always make people laugh"
else:
    print("Invalid choice")
    exit()

chatHistory = [
    SystemMessage(content=role)
]

while True:

    user_prompt = input("You : ")
    chatHistory.append(HumanMessage(content=user_prompt))
    response = model.invoke(chatHistory)
    chatHistory.append(AIMessage(content=response.content))
    print("AI : ",response.content)

