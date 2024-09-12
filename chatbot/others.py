import os
import ast
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
import sqlalchemy as sa
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from .constant import MODEL_NAME, EMBEDDINGS_MODEL
from .templates import GET_RELATED_SKILL_TEMPLATE, GET_SKILL_DESCRIPTION_TEMPLATE
from .queries import GET_SKILL_BY_MY_NAME_QUERY, GET_EMPLOYEE_BY_EMBEDDING
from .database_utils.read_operation import get_postgres_conn, get_stored_skills

load_dotenv()
output_parser = StrOutputParser()
openai_api_key = os.getenv('OPENAI_API_KEY')
model_name = os.getenv("MODEL_NAME")
client = OpenAI()


def save_conversation_in_database(conversation):
    """Save chat history to the database with the current timestamp."""
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO botservice_chathistory (message, response, timestamp, employee_id_id)
            VALUES (%s, %s, %s, %s)
            """, (conversation["message"], conversation["response"], datetime.now(), conversation["employee_id_id"]))
        conn.commit()
        logging.info("Conversation saved successfully.")
    except Exception as e:
        logging.info("\nAn error occurred, save_conversation_in_database:", e)
        return None


def get_embedding(text, model=EMBEDDINGS_MODEL):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def find_most_similar_employee(name, employees_name, threshold = 0.6):
    try:
        name_embedding = get_embedding(name.lower())
        conn = get_postgres_conn()
        cursor = conn.cursor()
        query = GET_EMPLOYEE_BY_EMBEDDING.format(name_embedding=name_embedding, threshold=threshold)
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            most_similar_employee = result[0]
        else:
            most_similar_employee = result

        return most_similar_employee
    except Exception as e:
        logging.info("\nAn error occurred, find_most_similar_employee:", e)
        return None


# def get_user_info(employee_id):
#     try:
#         conn = get_postgres_conn()
#         cursor = conn.cursor()
#         query = GET_SKILL_BY_MY_NAME_QUERY.format(name=employee_id) ######
#         cursor.execute(query)
#         temp = pd.read_sql(query, conn)
#         user_info = temp.to_dict(orient='records')
#         return user_info
#     except Exception as e:
#         logging.info("\nAn error occurred, find_most_similar_employee:", e)
#         return None


def get_skill_description(skill):
    try:
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", GET_SKILL_DESCRIPTION_TEMPLATE.format(skill_name=skill)),
            ("user", "{question}")
        ])
        chain = prompt | llm | output_parser
        desc = chain.invoke({"question": f"{skill}"})
        return desc
        
    except Exception as e:
        logging.error("An error occurred, get_skill_description_embedding:", e)
        return None

