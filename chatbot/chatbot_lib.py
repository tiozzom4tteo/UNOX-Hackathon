import os
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain


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


def get_memory(st_callback):  # create memory for this chat session

    # ConversationSummaryBufferMemory requires an LLM for summarizing older messages
    # this allows us to maintain the "big picture" of a long-running conversation
    llm = get_llm(st_callback)

    # Maintains a summary of previous messages
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1024)

    return memory


def get_chat_response(prompt, memory, streaming_callback):  # chat client function

    llm = get_llm(streaming_callback)

    conversation_with_summary = ConversationChain(  # create a chat client
        llm=llm,  # using the Bedrock LLM
        memory=memory,  # with the summarization memory
        verbose=True  # print out some of the internal states of the chain while running
    )

    # pass the user message and summary to the model
    chat_response = conversation_with_summary.predict(input=prompt)

    return chat_response
