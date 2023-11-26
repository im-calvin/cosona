from flask import Flask, request
import cohere
from pymongo import MongoClient
from dotenv import load_dotenv
import pprint
from co import *
import os
from bson.objectid import ObjectId
import gridfs
from constants import COLLECTION_NAME, PROMPTS
from langchain.chat_models import ChatCohere
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from flask_cors import CORS
from langchain.chat_models import ChatCohere
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chat_models import ChatCohere
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
import json

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://cosona.vercel.app"])
dbClient = MongoClient(os.getenv("ATLAS_URI"))
cohere_db = dbClient[os.getenv("DB_NAME")]
printer = pprint.PrettyPrinter(indent=4)
co = cohere.Client(os.getenv("COHERE_API_KEY"))
chat_model = ChatCohere(
    cohere_api_key=os.getenv("COHERE_API_KEY"), model="command", temperature="0.5"
)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/api/characters", methods=["GET"])
def get_characters():
    # gets a list of characters from the pdf, requires the fileId as a query parameter
    fileId = request.args.get("fileId")
    if fileId is None:
        return {"error": "Please provide a fileId"}

    # try to get the file from gridfs
    fs = gridfs.GridFS(database=cohere_db, collection=COLLECTION_NAME)
    fs_file = ObjectId(fileId)
    if not fs.exists(fs_file):
        return {"error": "File not found"}
    pdf_file = fs.get(fs_file)

    if pdf_file is None:
        return {"error": "File not found"}

    # this doesn't scale
    filename = "output.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_file.read())

    text = get_pdf_text(filename)

    characters = get_character_list(os.getenv("COHERE_API_KEY"), text)

    return {"characters": characters}


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    chat_history = data["text"]
    character = data["character"]
    if character == "":
        return {"error": "Please select a character"}
    response = get_response(chat_history, character)

    return response


def get_response(messages, character):
    prompt_template = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(PROMPTS[character]),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),  # last message
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation = LLMChain(
        llm=chat_model, prompt=prompt_template, verbose=True, memory=memory
    )

    response = conversation.invoke({"input": PROMPTS[character] + messages[-1]})

    # Return the response
    res = {
        "message": response["text"],
    }

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
