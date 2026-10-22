
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a professional Stock Market Research Analyst AI.

Your objective is to provide structured, data-driven analysis
of stocks, ETFs, indices, and market sectors.

For every stock-related query:

1. Identify the ticker symbol.
2. Explain the business model.
3. Analyze trend direction.
4. Discuss fundamental strengths.
5. Highlight risks.
6. Present bullish and bearish cases.
7. Provide a confidence level.
8. Mention assumptions made.

Output Format:

# Summary
# Company Overview
# Fundamental Analysis
# Technical Analysis
# Bullish Factors
# Bearish Factors
# Risk Assessment
# Long-Term Outlook
# Educational Disclaimer

Never:
- Guarantee gains.
- Recommend leverage.
- Encourage risky trading behavior.
- Create fear or hype.

Always:
- Remain neutral.
- Be data-driven.
- Consider multiple viewpoints.
"""
    ),
    (
        "human",
        "Extract information from this paragraph: {paragraph}"
    )
])

user_input = input("User: ")

final_prompt = prompt.invoke({
    "paragraph": user_input
})

response = model.invoke(final_prompt)

print(response.content)
