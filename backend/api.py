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
import re

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


@app.route("/api/characters", methods=["POST"])
def get_characters():
    # gets a list of characters from the pdf, requires the file in the request (formdata)
    # return {"characters": ["Harry Potter", "Ron Weasley", "Hermione Granger"]}
    if "file" not in request.files:
        return {"error": "No file provided"}

    file = request.files["file"]

    if file.filename == "":
        return {"error": "No filename"}

    text = get_pdf_text(file)

    characters = get_character_list(os.getenv("COHERE_API_KEY"), text)
    # remove all the text including the . from the last element in the array ("\n\nWould you like to know more about any of these characters?"")

    characters = characters[:-1]

    pattern = r"\n\n.*"
    modified_char = re.sub(pattern, "", characters[-1])

    print(modified_char)
    characters.append(modified_char)
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
    # if there's a preset prompt for the character, use it
    if character in PROMPTS:
        prompt = PROMPTS[character]
    else:
        prompt = generate_prompt(character)

    prompt_template = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),  # last message
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation = LLMChain(
        llm=chat_model, prompt=prompt_template, verbose=True, memory=memory
    )
    response = conversation.invoke({"input": prompt + messages[-1]})

    print(response["text"])
    # Return the response
    res = {
        "message": response["text"],
    }

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
