from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

LLM_TYPE = {
    "OLLAMA": ChatOllama,
    "OPENAI": ChatOpenAI,
    "ANTHROPIC": ChatAnthropic,
    "GEMINI": ChatGoogleGenerativeAI,
    "GROQ": ChatGroq,
    # Future LLM integrations can be added here
}