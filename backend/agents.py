import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import ReadFinancialDocumentTool

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

llm = LLM(
    provider="gemini",
    api_key=API_KEY,
    model="gemini-2.5-flash",
    project="gen-lang-client-0931582473",
    location="us-central1"
)

# response = llm.run("Hello world!")  # FIXED LINE
# print(response)

tools = [ReadFinancialDocumentTool()]

financial_analyst = Agent(
    role="Financial Analyst",
    goal="Extract and summarize key metrics from financial reports.",
    backstory="A cautious analyst who avoids hallucination and states uncertainty clearly.",
    tools=tools,
    llm=llm,
    max_iter=3,
    allow_delegation=False
)
