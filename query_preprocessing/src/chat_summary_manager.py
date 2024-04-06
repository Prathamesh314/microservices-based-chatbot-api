from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import (
    RunnableLambda,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.globals import set_debug
import os
from dotenv import find_dotenv, load_dotenv
import enum
import pydantic
from typing import List

from .redis_manager import Message, MessageRole

set_debug(True)

load_dotenv(find_dotenv())
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class Model(str, enum.Enum):
    gemini_pro = "gemini-pro"
    llama2 = "llama2"
    llama2_uncensored = "llama2-uncensored"


class Query(pydantic.BaseModel):
    question: str
    model: Model

summarization_prompt_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        SystemMessage(
            content="Summarise the chat. include as much detail as much details in the least words possible such that it is easy to understand the context."
            # content="You are an AI assistant with the capability to process summaries of conversations and related follow-up questions. Your task is to rephrase a given follow-up question so it can be understood as a standalone question, without needing additional context from the conversation summary. Ensure the rephrased question maintains the essence and specificity of the original query, allowing for clear and concise communication. Given below is the example of what kind of response is expected"
            # content="You are an AI assistant specialized in reading transcripts of conversation between human and AI. Your primary task is to provide brief, accurate summaries of these transcripts, ensuring no important details are omitted."
        ),
    ]
)


def summary_chain(llm):
    summarization_chain = (
        RunnableLambda(
            lambda x: PromptTemplate(
                template=summarization_prompt_template.invoke(x).to_string(),
                input_variables=[],
            ).invoke({})
        )
        | llm
        | StrOutputParser()
    )

    def get_summary(x):
        def get_history_object(mesg):
            if mesg.role == MessageRole.assistant:
                return AIMessage(mesg.content)
            else:
                return HumanMessage(mesg.content)

        history = x["history"]

        if len(history) > 0:
            return summarization_chain.invoke(
                {"history": list(map(get_history_object, history))}
            )
        else:
            return "None"

    return RunnableLambda(get_summary)


class ChatSummaryManager:
    def __init__(self, model, temperature):
        self.model = model
        self.temperature = temperature

        match model:
            case Model.gemini_pro:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model,
                    temperature=self.temperature,
                    convert_system_message_to_human=True,
                )
            case _:
                raise RuntimeError(f"unimplemented model type {model}")

    def summarize_chats(self, history: List[Message]) -> str:
        chain = summary_chain(self.llm)
        return chain.invoke({"history": history})


def get_chat_summary_manager(
    model: Model, temperature: float = 0.5
) -> ChatSummaryManager:
    return ChatSummaryManager(model=model, temperature=temperature)
