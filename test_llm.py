from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()  # .env dosyasindaki key'i okur

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

response = llm.invoke("Merhaba, sen kimsin? Tek cümle cevap ver.")
print(response.content)