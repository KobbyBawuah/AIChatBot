import os
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from dotenv import load_dotenv
import openai
from colorama import Fore, Back, Style
import sentry_sdk
import streamlit as st
from PyPDF2 import PdfReader

sentry_sdk.init(
  dsn="https://5a87e033b27340fe82b9c0a6a0eb93fc@o1145044.ingest.sentry.io/4505588043284480",

  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  # We recommend adjusting this value in production.
  traces_sample_rate=1.0
)

load_dotenv()

#Get Key
openai.api_key = os.getenv("OPENAI_API_KEY")

#test
# division_by_zero = 1 / 0

def get_moderation(question):
  """
  Check if the question is safe to ask the model

  Parameters:
    question (str): The question to check

  Returns a list of errors if the question is not safe, otherwise returns None
  """

  errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
  }
  response = openai.Moderation.create(input=question)
  if response.results[0].flagged:
      # get the categories that are flagged and generate a message
      result = [
        error
        for category, error in errors.items()
        if response.results[0].categories[category]
      ]
      return result
  return None

def get_response(index, previous_questions_and_answers, new_question):
  
  """Get a response after querrying the created vector after the question is absorbed

  Args:
    index: creates an index using the VectorstoreIndexCreator class, initialized with text data loaded from a document loader
    previous_questions_and_answers: Chat history
    new_question: The new question to ask the bot

  Returns:
    The response text
  """
  #Consider limiting the previous question limit to the last 10. 

  messages = ""
  messages += previous_questions_and_answers
  messages += "Human: " + new_question
  messages += "AI: " 

  # print("Message to send: ------->",messages)

  # print("New question posed: ------->",new_question)

#If you want to use outside data in conjuction with the internal data, pass in a language model like this
#print(index.query(query,llm=ChatOpenAI()))
#Current implimentation should only send the standalone question to vector store as oposed to the LLM model. 
  # result = index.query(messages)
  result = "Demo data"
  # print("Response: -------->",result)

  return result

def main():
  #UI
    st.set_page_config(page_title="Ask your File")
    st.header("Ask your PDF or Text file 💬")

    file_type = ["pdf", "txt"]
    text_content = ""

    #upload the file
    uploaded_file = st.file_uploader("Upload your PDF or Text", type=file_type)

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension.lower() == "pdf":
            # Handle PDF file
            st.write("You uploaded a PDF file!")
            # Process the PDF file 
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            st.write(text_content)

        elif file_extension.lower() == "txt":
            # Handle text file
            st.write("You uploaded a text file.")
            # Process the text file 
            text_content = uploaded_file.getvalue().decode("utf-8")
            st.write(text_content)

        else:
            st.error("Unsupported file type! Please upload a PDF or text file.")

    previous_questions_and_answers = ""

    # #Text loader
    # loader = TextLoader('constitution.txt')
    # # print ("rahh 1")

    # # loader = DirectoryLoader(".", glob="*.txt")
    
    
    
    # index = VectorstoreIndexCreator().from_loaders([text_content])
    # st.write("vector created!!!")

    # while True:
    #     # ask the user for their question
    #     new_question = input(
    #         Fore.GREEN + Style.BRIGHT + "How can I help you?: " + Style.RESET_ALL
    #     )
    #     # check the question is safe
    #     errors = get_moderation(new_question)
    #     if errors:
    #             print(
    #                 Fore.RED
    #                 + Style.BRIGHT
    #                 + "Sorry, you're question didn't pass the moderation check:"
    #             )
    #             for error in errors:
    #                 print(error)
    #             print(Style.RESET_ALL)
    #             continue
        
    #     response = get_response(index, previous_questions_and_answers, new_question)

    #     previous_questions_and_answers+="Human: " + new_question + " " + "AI: " + response + " "

    #     # print the response
    #     print(Fore.CYAN + Style.BRIGHT + "Here you go: " + Style.NORMAL + response)

if __name__ == "__main__":
    main()