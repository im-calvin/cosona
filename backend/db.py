import gridfs
from werkzeug.datastructures import FileStorage
from constants import *
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


def store_pdf(filepath):
    # Create a GridFS object
    # this connects to mongo
    dbClient = MongoClient(os.getenv("ATLAS_URI"))
    cohere_db = dbClient[os.getenv("DB_NAME")]
    fs = gridfs.GridFS(database=cohere_db, collection=COLLECTION_NAME)

    with open(filepath, "rb") as f:
        # Store the binary data in GridFS
        pdf_id = fs.put(f, filename=filepath)

    return pdf_id


if __name__ == "__main__":
    store_pdf("pdfs/Fast-Five-2011.pdf")
