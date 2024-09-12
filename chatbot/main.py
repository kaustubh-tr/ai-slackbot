import os
import logging
import psycopg2
import langchain
langchain.debug=False
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate as SystemTemplate,
    HumanMessagePromptTemplate as HumanTemplate,
    MessagesPlaceholder,
)
from langchain.agents import Tool, initialize_agent, AgentType, create_openai_tools_agent, AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime

from .constant import MODEL_NAME
from .queries import GET_SKILL_BY_MY_NAME_QUERY
from .templates import SYSTEM_MESSAGE, USER_QUESTION_TEMPLATE
from .tools.search_manager import get_employee_by_skill_tool, get_skill_by_employee_tool
from .tools.skill_manager import set_employee_details_tool, remove_employee_details_tool
from .tools.vector_db import get_vector_db_search_tool
from .database_utils.read_operation import get_chat_history, get_postgres_conn, get_stored_skills, get_user_info
from .others import save_conversation_in_database

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

class SlackBot:
    def __init__(self):
        self.llm = self.get_llm()

    def get_llm(self):
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, max_tokens=1000)
        return llm

    def get_tool_list(self, question, employee_id, bot_id) -> list:
        employee_by_skill_search_tool = get_employee_by_skill_tool(employee_id)
        skill_by_employee_search_tool = get_skill_by_employee_tool(employee_id, bot_id)
        save_employee_details_tool = set_employee_details_tool(employee_id)
        delete_employee_details_tool = remove_employee_details_tool(employee_id)
        vector_db_search_tool = get_vector_db_search_tool(question)
        return [
            employee_by_skill_search_tool,
            skill_by_employee_search_tool,
            save_employee_details_tool,
            delete_employee_details_tool,
            vector_db_search_tool
        ]

    def get_response(self, question, employee_id, bot_id):
        try:
            if employee_id is not None:
                user_info = get_user_info(employee_id)
                system_message_template = SystemTemplate.from_template(SYSTEM_MESSAGE)
                system_message = system_message_template.format(user_info=user_info)
                history = self.add_chat_history_to_agent(employee_id)  
                agent_kwargs = {
                    "system_message": system_message,
                    "extra_prompt_messages": history.messages,
                }
                # prompt = hub.pull("hwchase17/openai-tools-agent")
                # prompt = ChatPromptTemplate.from_messages(
                #     [
                #         SystemTemplate(
                #             prompt=PromptTemplate(input_variables=[], template=SYSTEM_MESSAGE)
                #         ),
                #         MessagesPlaceholder(variable_name="chat_history", optional=True),
                #         HumanTemplate(
                #             prompt=PromptTemplate(
                #                 input_variables=["question"],
                #                 template=USER_QUESTION_TEMPLATE,
                #             )
                #         ),
                #         MessagesPlaceholder(variable_name="agent_scratchpad"),
                #     ]
                # )
                tools = self.get_tool_list(question, employee_id, bot_id)
                agent = initialize_agent(
                    tools=tools,
                    llm=self.llm,
                    agent=AgentType.OPENAI_FUNCTIONS,
                    verbose=True,
                    agent_kwargs=agent_kwargs,
                    return_intermediate_steps=True
                )
                # agent = create_openai_tools_agent(llm, tools, prompt)
                # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
                # answer = agent_executor.invoke(
                #     {
                #         "question": question,
                #         "chat_history": history.messages,
                #     }
                # )
                answer = agent.invoke(question)
                save_conversation_in_database({
                    "message": question,
                    "response": answer['output'],
                    "employee_id_id": employee_id
                })
                return answer
    
            else:
                no_information_msg = "It seems like I don't have any information about you. Please save your details by using the below command, so that I can provide you with personalized assistance: ```/save-user-info```"
                return no_information_msg

        except Exception as e:
            no_answer = "Sorry, I am unable to answer this question."
            return no_answer


    def add_chat_history_to_agent(self, employee_id) -> ChatMessageHistory:
        chat_history = get_chat_history(employee_id)
        if chat_history is None:
            chat_history = []

        history = ChatMessageHistory()
        for chat in chat_history:
            history.add_user_message(chat[1])
            history.add_ai_message(chat[2])
        return history


if __name__ == "__main__":
    chat_bot = SlackBot()