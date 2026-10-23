
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Literal, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class Stock(BaseModel):
    stock_name: str
    analysis_for: Optional[str] = None
    current_price: float

    trend: Literal["bullish", "bearish", "sideways"]
    recommendation: Literal["buy", "hold", "sell"]

    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    risk_level: Literal["low", "medium", "high"]

    analysis_summary: str


parser = PydanticOutputParser(pydantic_object=Stock)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert financial analyst.
        Analyze the user's request and return a stock analysis.

        Include:
        - Stock name
        - Analysis period
        - Current price
        - Trend
        - Recommendation
        - Target price
        - Stop loss
        - Risk level
        - Analysis summary

        Do not invent current market prices.
        If reliable price data is unavailable, do not guess.

        {format_instructions}
        """
    ),
    ("human", "{paragraph}")
])

para = input("Give your paragraph: ")

final_prompt = prompt.invoke({
    "paragraph": para,
    "format_instructions": parser.get_format_instructions()
})

response = model.invoke(final_prompt)

stock_data = parser.parse(response.content)

print(stock_data)
print(stock_data.model_dump())
