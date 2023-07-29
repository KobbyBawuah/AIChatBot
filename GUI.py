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
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings 
# from langchain.vectorstores import FAISS

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
  result = index.query(messages)
#   result = "Demo data"
  # print("Response: -------->",result)

  return result


def write_text_to_file(file_name, text_to_write):
    try:
        # Step 1: Open/create the file in write mode
        with open(file_name, 'w') as file:
            # Step 2: Write the desired text into the file
            file.write(text_to_write)
        print("Text has been successfully written to the file.")
    except Exception as e:
        print(f"Error: {e}")

def question_and_answer_generation(index, previous_questions_and_answers):
    user_question = st.text_input("Ask a question about your document:")
    if user_question:
        errors = get_moderation(user_question)
        if errors:
            st.write("Sorry, you're question didn't pass the moderation check:")
            for error in errors:
                st.write(error)
                st.write(Style.RESET_ALL)

        response = get_response(index, previous_questions_and_answers, user_question)

        previous_questions_and_answers += "Human: " + user_question + " " + "AI: " + response + " "

        st.write(response)

def create_index(name):
    text_loader = TextLoader(name)
    index = VectorstoreIndexCreator().from_loaders([text_loader])

    return index


def main():
  #UI
    st.set_page_config(page_title="Ask your File")
    st.header("Ask your PDF or Text file 💬")

    file_type = ["pdf", "txt"]
    text_content = ""
    previous_questions_and_answers = ""
    file_uploaded = False
    index = None


    #upload the file
    uploaded_file = st.file_uploader("Upload your PDF or Text file", type=file_type)

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension.lower() == "pdf":
            # Handle PDF file
            st.write("You uploaded a PDF file!")

            # Process the PDF file 
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text_content += page.extract_text()

            #Implementation for the VectorstoreIndexCreator() way
            
            #Change to text file
            write_text_to_file(uploaded_file.name, text_content)           

            #create index
            index = create_index(uploaded_file.name)

            os.remove(uploaded_file.name)
            print("File has been successfully deleted.")

            # #Alternative to simply calling VectorstoreIndexCreator() below

            # #split into chuncks 
            # text_splitter = CharacterTextSplitter(
            #     separator="\n",
            #     chunk_size=1000,
            #     chunk_overlap=200,
            #     length_function=len
            # )

            # chunks = text_splitter.split_text(text_content)

            # st.write(chunks)

            # #create embeddings
            # embeddings = OpenAIEmbeddings()
            # knoweldge_base = FAISS.from_texts(chunks,embeddings)

            ## then query the knowledge base with any language model on something like docs = knoweldge_base.similarity_search(user_question)

            st.write("-------->>>>>>>>>PDF vector created!!!")
            
            question_and_answer_generation(index, previous_questions_and_answers)

        elif file_extension.lower() == "txt":
            # Handle text file
            st.write("You uploaded a text file.")
            # Process the text file 
            text_content = uploaded_file.getvalue().decode("utf-8")
            # st.write(text_content)

            #create index
            index = create_index(uploaded_file.name)

            st.write("-------->>>>>>>>>Text vector created!!!")
            question_and_answer_generation(index, previous_questions_and_answers)
            
        else:
            st.error("Unsupported file type! Please upload a PDF or text file.")

if __name__ == "__main__":
    main()