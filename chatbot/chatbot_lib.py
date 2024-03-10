import os
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.chains import ConversationalRetrievalChain

from langchain.embeddings import BedrockEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase

from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool



def get_llm(streaming_callback):

    model_kwargs = {
        "max_tokens": 4000,
        "temperature": 0,
        "p": 0.01,
        "k": 0,
        "stop_sequences": [],
        "return_likelihoods": "NONE",
        "stream": True
    }

    llm = Bedrock(
        credentials_profile_name=os.environ.get("default"),
        region_name='us-east-1',  # sets the region name (if not the default)
        model_id="cohere.command-text-v14",
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[streaming_callback],
    )

    return llm


def get_index(pdf_path):  # creates and returns an in-memory vector store to be used in the application

    embeddings = BedrockEmbeddings(
        # sets the profile name to use for AWS credentials (if not the default)
        credentials_profile_name=os.environ.get("default"),
        # sets the region name (if not the default)
        region_name='us-east-1',
        # sets the endpoint URL (if necessary)
    )  # create a Titan Embeddings client

    # assumes local PDF file with this name
    # pdf_path = "2022-Shareholder-Letter.pdf"

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


def get_memory(st_callback, flag):  # create memory for this chat session

    if flag == 1:
        llm = get_llm(st_callback)
        memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1024)
    elif flag == 2:
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history", return_messages=True)

    return memory


# rag response
def get_chat_response_rag(prompt, memory, streaming_callback, index):

    llm = get_llm(streaming_callback)

    conversation_with_retrieval = ConversationalRetrievalChain.from_llm(
        llm, index.vectorstore.as_retriever(), memory=memory, verbose=True)

    # pass the user message, history, and knowledge to the model
    chat_response = conversation_with_retrieval({"question": prompt})

    return chat_response['answer']


def get_chat_response(prompt, memory, streaming_callback):  # chat client function

    db = SQLDatabase.from_uri("sqlite:///ovensUnox.db")
    llm = get_llm(streaming_callback)
    chain = create_sql_query_chain(llm, db)

    response = chain.invoke({"question": prompt})
    

    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    chain = write_query | execute_query
    chain.invoke({"question": "How many employees are there"})
    
    print(chain.invoke({"question": "How many employees are there"}))

    # return response['answer']

    # conversation_with_summary = ConversationChain(  # create a chat client
    #     llm=llm,  # using the Bedrock LLM
    #     memory=memory,  # with the summarization memory
    #     verbose=True  # print out some of the internal states of the chain while running
    # )

    # # pass the user message and summary to the model
    # chat_response = conversation_with_summary.predict(input=prompt)

    # return chat_response
