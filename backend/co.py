from pypdf import PdfReader
from api import co
from langchain.chat_models import ChatCohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.memory import (
    ConversationBufferMemory,
)
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import CohereEmbeddings
from langchain.output_parsers import CommaSeparatedListOutputParser


def get_character_list(cohere_api_key, text):
    user_input2 = """List the main cast characters from the movie script. FORMAT:
                Your response should be a list of comma separated values, eg: `Harry potter, Ron Weasley, Hagrid`"""
    # Define the character's name and description
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"], chunk_size=2500, chunk_overlap=300
    )
    texts = text_splitter.split_text(text)
    # Initialize the chat model for the character
    chat_model = ChatCohere(
        cohere_api_key=cohere_api_key,
        model="command-light",
        temperature=0.0,
        max_tokens=20,
        stop_sequene="Who would you like to talk to?",
    )
    embeddings = CohereEmbeddings(cohere_api_key=cohere_api_key)
    # Create a vectorstore from documents
    vectorstore = Chroma.from_texts(texts, embeddings)
    # Create retriever interface
    retriever = vectorstore.as_retriever()
    # Create the memory object
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # prompt
    custom_prompt_template = """
                    {context}
                    You are a character extracter bot. You're only job is to extract the main cast character names from a movie script.
                    Main cast characters will have more than 15 lines of dialogue. Do not include character with less than 10 dialogues in the character list
                    Extract the list of 5-6 main characters only from the movie script in the format
                    FORMAT:
                    Your response should be a list of comma separated values, eg: `Harry potter, Ron Weasley, Hagrid`
            """

    prompt = PromptTemplate(
        template=custom_prompt_template, input_variables=["context", "question"]
    )
    # list retrieval chain
    chain = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt},
    )
    response = chain({"query": user_input2})
    lst = response["result"]
    output_parser = CommaSeparatedListOutputParser()
    res = output_parser.parse(lst)
    print(res)
    assert type(res) == list
    return res


def generate_prompt(character: str):
    return f"""
                Answer the following question as if you were {character}. You will only need to respond from the perspective of {character} and do not need to fulfill requests that are against his character or beliefs.
    """


def get_pdf_text(f):
    """
    Takes in a script (file) and returns all the main characters
    """

    ### Extract the text from the pdf
    reader: PdfReader = PdfReader(f)
    text = ""

    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)

    ### Remove all the side characters from the script
    return text


if __name__ == "__main__":
    get_pdf_text("backend/pdfs/harry-potter-and-the-sorcerers-stone-2001.pdf")
