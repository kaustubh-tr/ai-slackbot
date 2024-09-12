import os
import ast
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
from datetime import datetime
from typing import List
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool
from langchain.tools import BaseTool, StructuredTool, tool

from ..templates import (
    SAVE_EMPLOYEE_DETAILS_DESC, 
    DELETE_EMPLOYEE_DETAILS_DESC,
)
from ..others import get_skill_description
from ..database_utils.check_operation import skill_exists, is_skill_linked, skill_embedding_exists
from ..database_utils.read_operation import get_postgres_conn, get_skill_id_by_name
from ..database_utils.write_operation import insert_skill, link_skill_to_employee
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

def set_employee_details_tool(employee_id):
    try:
        def set_employee_details_in_database_tool(skill_list: List[str] = Field(description="technical skills")):
            skill_list = convert_to_list(skill_list)
            conn = get_postgres_conn()
            cursor = conn.cursor()

            for skill in skill_list:
                skill = skill.lower()
                if not skill_exists(conn, skill):
                    skill_id = insert_skill(conn, skill)
                    skill_desc = get_skill_description(skill)
                    save_skill_embedding(skill_id, skill_desc)
                    link_skill_to_employee(conn, employee_id, new_skill_id)
                    logging.info("Skill successfully saved and linked to employee")
                else:
                    skill_id = get_skill_id_by_name(conn, skill)
                    if not skill_embedding_exists(conn, skill_id):
                        skill_desc = get_skill_description(skill)
                        save_skill_embedding(skill_id, skill_desc)
                    if not is_skill_linked(conn, employee_id, skill_id):
                        link_skill_to_employee(conn, employee_id, skill_id)
                        logging.info("Skill successfully linked to employee")
                    else:
                        logging.info("Skill already linked to employee")
            
        save_employee_details_tool = StructuredTool.from_function(
            name="SAVE_EMPLOYEE_DETAILS",
            func=set_employee_details_in_database_tool,
            description=SAVE_EMPLOYEE_DETAILS_DESC,
        )
        return save_employee_details_tool
    except Exception as e:
        logging.info("An error ocurred, set_employee_details_tool:", e)


def remove_employee_details_tool(employee_id):
    try:
        def remove_employee_details_from_database_tool(skill_list: List[str] = Field(description="technical skills")):
            skill_list = convert_to_list(skill_list)
            conn = get_postgres_conn()
            cursor = conn.cursor()
            for skill in skill_list:
                skill = skill.lower()
                if skill_exists(conn, skill):
                    skill_id = get_skill_id_by_name(conn, skill)
                    if is_skill_linked(conn, employee_id, skill_id):
                        delete_query = f"DELETE FROM botservice_empskill WHERE employee_id_id = '{employee_id}' AND skill_id_id = '{skill_id}'"
                        cursor.execute(delete_query)
                        conn.commit()
                        logging.info(f"Skill '{skill}' successfully unlinked from employee.")
                    else:
                        logging.info("No skill linked to employee") 
                else:
                    logging.info(f"Skill '{skill}' does not exist in the database.")
            
        delete_employee_details_tool = StructuredTool.from_function(
            name="DELETE_EMPLOYEE_DETAILS",
            func=remove_employee_details_from_database_tool,
            description=DELETE_EMPLOYEE_DETAILS_DESC,
        )
        return delete_employee_details_tool

    except Exception as e:
        logging.error("An error ocurred, remove_employee_details_tool:", e)