from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel
import json
from dotenv import load_dotenv, find_dotenv
from .create_llm import CreateLLM
from .chat_summary_manager import Model

load_dotenv(find_dotenv())

# guard_prompt = """
# System: you are an AI. your job is to check if the given prompt is related to medical info in any way. DO NOT answer the query. you must output it in json format. {{{{ "related": "no", "reason": <INSERT REASONING HERE> }}}} or {{{{ "related": "yes", "reason": <INSERT REASONING HERE> }}}}

# Context: user tells AI that they fell on their knee on a playground and hurt themselves.
# Prompt: How do i treat it?
# Output: {{{{ "related": "yes", "reason": "user wants to know how to treat a knee wound" }}}}

# Context: user tells AI they they have cough.
# Prompt: How do i complete the first level of mario?
# Output: {{{{ "related": "no", "reason": "user want information about mario. not related to any medical context" }}}}

# Context: {context}
# Prompt: {prompt}
# Output: 
# """
guard_prompt = """
You are an AI which is built to classify whether a given query is related to medical in any sense or not. Do not answer the query,
just classify it as 'YES', 'NO', 'MAYBE', or 'ILLEGAL'. If you think the given query is related to medical then answer will be 'YES'.
If you think the given query is not related to medical then output 'NO'. If you are are 70 percent sure that this can be related to medical
by any sense like whether it requires any medical treatment or doctor supervision then output 'MAYBE' else your answer.
You must output an JSON consisting of 2 parameters:- 1) related 2) reason. Output this :- {{"related":"YES", "reason":"<Insert-Your-Reason-Here>"}} or {{"related":"NO","reason":"<Insert-Your-Reason-Here">}}.
The value of related will be either yes or no or maybe. The value of reason will the reason that will be inferred by you that why do you think
that it's answer is yes, no or maybe. You should have a valid reason to judge the query. donot hallucinate. if you cannot infer anything just output 'MAYBE'.
I will give you an example for the current situation.

1. first situation:-
query: I hurt myself while playing football
AI response: {{"related":"YES", "reason": "User wants to know how to treat a wound they got while playing"}}

2. second situation:-
query: I want to know best restaurant near me.
AI response: {{"related":"NO", "reason": "User is asking for restaurant, it is not related to medical field by any context"}}

If user is asking you about wrong practices which are related to medical field but they illegal, then output 'ILLEGAL'.
Wrong practices includes planning a murder of someone, asking about torturing someone using medical toolkits, something like this.

3. third situation:-
User: I want to take revenge with someone who always bully me in school. I want to set a trap for him like jigsaw and torture him with medical toolkits
AI response: {{"related":"ILLEGAL", "reason": "User is asking for wrong practices. I donot support helping or promoting such actions"}}

Query: {query}
AI response:
"""
# guard_prompt_template = PromptTemplate(
#     template=guard_prompt,
#     input_variables=["context", "prompt"]
# )

# def guard_chain(llm):
#     return (
#         RunnableParallel(context=lambda x: x["summary"], prompt=lambda x: x["question"])
#         | RunnableLambda(
#             lambda x: PromptTemplate(
#                 template=guard_prompt_template.invoke(x).to_string(),
#                 input_variables=[],
#             ).invoke({})
#         )
#         | llm
#         | StrOutputParser()
#     )


class GuardRails:

  def __init__(self, message: str):
    self.message = message

  def create_llm_chain(self):
    llm = CreateLLM.get_llm(model=Model.gemini_pro).llm
    chain = PromptTemplate.from_template(guard_prompt) | llm
    return chain

  def is_relevent(self):
    # Creating a llm chain
    chain = self.create_llm_chain()

    # Fetching response
    response = chain.invoke({"query": self.message})

    # Converting response to json format
    response = json.loads(response)

    related = response["related"]
    reason = response["reason"]
    if related == "NO":
        return {"ai_response": f"The message you asked is out of context. Reason: {reason}", "is_relevant": "NO"}

    elif related == "ILLEGAL":
        return {"ai_response": f"The message you asked sounds like wrong practices to me. I refuse to support such practices. Reason I think it is malicious: {reason}", "is_relevant": "ILLEGAL"}
    else:
        return {"ai_response": "-", "is_relevant": "YES"}

    # def check_if_fine(self, query: Query) -> bool:
    #     chain = guard_chain(self.llm)
    #     resp = chain.invoke(query.dict())

    #     try:
    #         resp = json.loads(resp)
    #         match resp["related"]:
    #             case "yes" | "maybe":
    #                 return True
    #             case "no":
    #                 return False
    #             case _:
    #                 return True
    #     except Exception:
    #         return True
