import os
import sys 
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

import sentry_sdk

sentry_sdk.init(
  dsn="https://5a87e033b27340fe82b9c0a6a0eb93fc@o1145044.ingest.sentry.io/4505588043284480",

  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  # We recommend adjusting this value in production.
  traces_sample_rate=1.0
)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("APIKEY")
# api_key = os.environ["OPENAI_API_KEY"]
# print(f"API KEY: {api_key}")

query = sys.argv[1]
print(query)

loader = TextLoader('constitution.txt')
# loader = DirectoryLoader(".", glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])

#If you want to use outside data in conjuction with the internal data, pass in a language model like this
#print(index.query(query,llm=ChatOpenAI()))
print(index.query(query))

#test
division_by_zero = 1 / 0