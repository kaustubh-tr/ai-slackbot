import os
import ast
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
import pandas as pd
import sqlalchemy as sa
from datetime import datetime
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool
from langchain.tools import BaseTool, StructuredTool, tool

from dotenv import load_dotenv
load_dotenv()
from ..database_utils.read_operation import get_postgres_conn, get_stored_skills, get_employees_name, get_slack_user_ids, get_skill_id_by_name
from ..others import find_most_similar_employee, get_embedding, get_skill_description
from ..queries import (
    GET_EMPLOYEE_BY_SKILL_QUERY, 
    SKILL_EXISTS_QUERY, 
    EMPLOYEE_EXISTS_QUERY, 
    GET_SKILL_BY_EMPLOYEE_QUERY,
    GET_SKILL_BY_EMBEDDING,
    GET_SKILL_EMBEDDING_QUERY,
)
from ..templates import (
    EMPLOYEE_SEARCH_BY_SKILL_DESC, 
    SKILL_SEARCH_BY_EMPLOYEE_DESC,
)
from ..embeddings.save_embedding import save_skill_embedding

def convert_to_list(skill_input):
    if isinstance(skill_input, list):
        return skill_input
    elif isinstance(skill_input, str):
        try:
            return ast.literal_eval(skill_input)
        except ValueError:
            return skill_input.split(", ")
    else:
        raise ValueError("Input must be either a list or a string")


def get_employee_by_skill_tool(employee_id):
    try:
        def get_employee_from_database_tool(skill: str = Field(description="skill")):
            threshold = 0.5
            stored_skills = get_stored_skills()
            conn = get_postgres_conn()
            cursor = conn.cursor()
            query = SKILL_EXISTS_QUERY.format(skill=skill)
            cursor.execute(query)
            skill_exists = cursor.fetchone()[0]
            if skill_exists:
                query = GET_SKILL_EMBEDDING_QUERY.format(skill=skill)
                cursor.execute(query)
                skill_embedding = cursor.fetchone()[0]

            else:
                skill_desc = get_skill_description(skill)
                skill_embedding = get_embedding(skill_desc)
            
            get_skill_query = GET_SKILL_BY_EMBEDDING.format(skill_embedding=skill_embedding, threshold=threshold)
            cursor.execute(get_skill_query)
            skills = [row[0] for row in cursor.fetchall()]

            results = []
            for skill in skills:
                query = GET_EMPLOYEE_BY_SKILL_QUERY.format(skill=skill, employee_id=employee_id)
                cursor.execute(query)
                temp = pd.read_sql(query, conn)
                results.extend(temp.to_dict(orient='records'))  # Extend the results list with temp
            return results
            
        employee_by_skill_search_tool = StructuredTool.from_function(
            name="EMPLOYEE_SEARCH_BY_SKILL",
            func=get_employee_from_database_tool,
            description=EMPLOYEE_SEARCH_BY_SKILL_DESC,
        )
        return employee_by_skill_search_tool

    except Exception as e:
        logging.error("An error occured, get_employee_by_skill_tool:", e)


def get_skill_by_employee_tool(employee_id, bot_id):
    try:
        def get_skill_from_database_tool(name: str = Field(description="name")):
            employees_name = get_employees_name()
            lower_name = name.lower()
            slack_user_ids = get_slack_user_ids()
            conn = get_postgres_conn()
            cursor = conn.cursor()

            # to handle for @GKM_IT_Bot as it will invoke as `bot_id`
            if name == f"<@{bot_id}>":
                return "I am a GKMIT Bot. My goal is to help people learn new skills and help them in their learning journey."
            
            # to handle for @person as it will invoke as `user_id`
            modified_slack_user_ids = ['<@' + lower_name + '>' for lower_name in slack_user_ids]
            if lower_name in modified_slack_user_ids:
                query = f"""SELECT e."full_name" FROM botservice_employee e WHERE e."slack_user_id" = '{name[2:-1]}';"""
                cursor.execute(query)
                name = cursor.fetchone()[0]
            else:
                query = EMPLOYEE_EXISTS_QUERY.format(name=name)
                cursor.execute(query)
                employee_exists = cursor.fetchone()[0]
                if not employee_exists:
                    most_similar_employee = find_most_similar_employee(name, employees_name)
                    logging.info(f"The most similar employee to '{name}' is '{most_similar_employee}'")
                    name = most_similar_employee
            
            query = GET_SKILL_BY_EMPLOYEE_QUERY.format(name=name)
            cursor.execute(query)
            temp = pd.read_sql(query, conn)
            return temp.to_dict(orient='records')

        skill_by_employee_search_tool = StructuredTool.from_function(
            name="SKILL_SEARCH_BY_EMPLOYEE",
            func=get_skill_from_database_tool,
            description=SKILL_SEARCH_BY_EMPLOYEE_DESC,
        )
        return skill_by_employee_search_tool

    except Exception as e:
        logging.error("An error occured, get_skill_by_employee_tool:", e)