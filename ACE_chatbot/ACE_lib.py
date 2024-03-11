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
import _sqlite3


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
    chat_response = conversation_with_retrieval({"question": {prompt}
                                                 })

    return chat_response['answer']


def get_chat_response(prompt, memory, streaming_callback):

    db = SQLDatabase.from_uri("sqlite:///dataNew.db")
    llm = get_llm(streaming_callback)
    chain = create_sql_query_chain(llm, db)

    # It generates a SQL query from the context and executes it on the database.
    response = chain.invoke({"question": """
        You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.
        Unless the user specifies in the question a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to use date('now') function to get the current date if the question involves "today".
        
        Use the following format:
        
        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here
        
        Database schema:
            table: oven
                list of attributes:
                    - unique_id: primary key
                    - brand: string with the oven's brand
                    - technology_type:
                    
        
        Examples:
        
        Question1: "Identificare il forno che consuma di più in base al tasso di ingresso"
        SQLQuery1: "SELECT brand, model_name, input_rate  FROM oven  ORDER BY input_rate DESC 
        LIMIT 1;"
        
        Question2: "Identificare il forno che consuma di meno in base al tasso di energia in 
        modalità di cottura a vapore inattivo"
        SQLQuery2: "SELECT brand, model_name, steam_idle_energy_rate  FROM oven 
        WHERE steam_idle_energy_rate IS NOT NULL  ORDER BY steam_idle_energy_rate  LIMIT 1;"
        
        Question3: "Identificare i forni che utilizzano un particolare tipo di combustibile"
        SQLQuery3:  "SELECT brand, model_name  FROM oven WHERE fuel_type = 'Gas';"
        
        Don't write the last row "SQLResult:"
                             
        Don't write the 'SQLQuery:'
        
        Question:""" + prompt})

    response = response[:response.find(";") + 1]

    print(response)

    con = _sqlite3.connect("ovensUnox.db")

    # query = "SELECT * FROM oven where 'Brand Name' == 'Unox'"

    cur = con.cursor()

    res = cur.execute(response)

    conversation_with_summary = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    stringa = prompt + "\n" + response + "\n" + """Context: 'You are a salesman and you are trying to send an oven to the customer who made the query. Use the SQL query to give the best answer to convince him'.  .
    you have to use {response}, {res} and {prompt} to answer the question with natural language, not other datas. Don't write the 'SQLQuery:'"""

    chat_response = conversation_with_summary.predict(input=stringa)

    print(chat_response)

    # It should transform the response into a human-readable format and return it.

    # answer_prompt = PromptTemplate.from_template(
    #     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    #     Question: {question}
    #     SQL Query: {query}
    #     SQL Result: {result}
    #     Answer: """
    #     )

    # write_query = create_sql_query_chain(llm, db)
    # execute_query = QuerySQLDataBaseTool(db=db)
    # print(write_query)
    # print(execute_query)
    # answer = answer_prompt | llm | StrOutputParser()
    # chain = (
    #     RunnablePassthrough.assign(query=write_query).assign(
    #         result=itemgetter(response) | execute_query
    #     )
    #     | answer
    # )
    # chain.invoke({"question": prompt})

    # conversation_with_summary = ConversationChain(  # create a chat client
    #     llm=llm,  # using the Bedrock LLM
    #     memory=memory,  # with the summarization memory
    #     verbose=True  # print out some of the internal states of the chain while running
    # )

    # # pass the user message and summary to the model
    # chat_response = conversation_with_summary.predict(input=prompt)

    return chat_response
