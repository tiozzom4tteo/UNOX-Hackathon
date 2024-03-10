# import os
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain.llms.bedrock import Bedrock
# from langchain.chains import ConversationChain

import os
import sqlite3
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationalRetrievalChain

from langchain.embeddings import BedrockEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase


postgres_user = "postgres"
postgres_password = ""
postgres_host = "localhost"
postgres_db = "tiozzomatteo"


def get_llm(streaming_callback):

    model_kwargs = {  # Anthropic's Claude model
        "maxTokenCount": 4000, 
        "stopSequences": [], 
        "temperature": 1, 
        "topP": 0.9, 
    }

    llm = Bedrock(
        credentials_profile_name=os.environ.get("default"),
        region_name="us-east-1",  # sets the region name (if not the default)
        model_id="amazon.titan-text-express-v1",
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[streaming_callback],
    )

    return llm


def get_index():  # creates and returns an in-memory vector store to be used in the application

    embeddings = BedrockEmbeddings(
        # sets the profile name to use for AWS credentials (if not the default)
        credentials_profile_name=os.environ.get("default"),
        # sets the region name (if not the default)
        region_name='us-east-1',
        # sets the endpoint URL (if necessary)
    )  # create a Titan Embeddings client

    # assumes local PDF file with this name
    pdf_path = "../document/prova.pdf"

    loader = PyPDFLoader(file_path=pdf_path)  # load the pdf file

    text_splitter = RecursiveCharacterTextSplitter(  # create a text splitter
        # split chunks at (1) paragraph, (2) line, (3) sentence, or (4) word, in that order
        separators=["\n\n", "\n", ".", " "],
        chunk_size=1000,  # divide into 1000-character chunks using the separators above
        chunk_overlap=100  # number of characters that can overlap with previous chunk
    )

    index_creator = VectorstoreIndexCreator(  # create a vector store factory
        vectorstore_cls=FAISS,  # use an in-memory vector store for demo purposes
        embedding=embeddings,  # use Titan embeddings
        text_splitter=text_splitter,  # use the recursive text splitter
    )

    # create an vector store index from the loaded PDF
    index_from_loader = index_creator.from_loaders([loader])

    return index_from_loader  # return the index to be cached by the client app


def get_memory():  # create memory for this chat session

    # Maintains a history of previous messages
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True)

    return memory


def get_chat_response(prompt, memory, index, streaming_callback):  # chat client function

    llm = get_llm(streaming_callback)

    conversation_with_retrieval = ConversationalRetrievalChain.from_llm(
        llm, index.vectorstore.as_retriever(), memory=memory, verbose=True)

    # pass the user message, history, and knowledge to the model
    chat_response = conversation_with_retrieval({"question": prompt})
    print(prompt)
    prova = "Utente: " + prompt + ". Crea una query in linguaggio sql per trovare il brand di nome 'Blodgett'"
    prova1 = conversation_with_retrieval({"question": prova})
    db = SQLDatabase.from_uri("sqlite:///ovens.db")


    print(db.dialect)
    print(prova1)

    

    return chat_response['answer']


# Aggiungi questa importazione alla parte superiore del tuo codice


def get_memory_from_database():
    # Modifica queste informazioni in base al tuo database
    database_path = 'ovens.db'
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Esempio di query per ottenere i dati dalla tabella 'memory'
    cursor.execute("SELECT * FROM ovens")
    memory_data = cursor.fetchall()
    print(memory_data)
    # Chiudi la connessione al database
    connection.close()

    return memory_data
