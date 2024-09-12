import os
import json
import uuid
import psycopg2
import threading
import logging
logging.basicConfig(level=logging.DEBUG)
from datetime import datetime
from langchain_community.llms import OpenAI
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from chatbot.queries import SKILL_EXISTS_QUERY
from chatbot.others import get_embedding, get_skill_description
from chatbot.database_utils.check_operation import employee_exists, skill_exists, is_skill_linked, skill_embedding_exists
from chatbot.database_utils.read_operation import get_postgres_conn, get_employee_id, get_skill_id_by_name, get_user_skills
from chatbot.database_utils.write_operation import insert_employee, insert_skill, link_skill_to_employee
from chatbot.embeddings.save_embedding import save_employee_embedding, save_skill_embedding

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_USER_TOKEN = os.getenv('SLACK_BOT_USER_TOKEN')
slack_client = WebClient(token=os.getenv('SLACK_BOT_USER_TOKEN'))


def parse_user_info(body):
    employee_data = {}
    skill_data = []
    slack_user_id = body['user']['id']
    for key, value in body['view']['state']['values'].items():
        if 'plain_text_input-action_1' in value:
            employee_data['first_name'] = value['plain_text_input-action_1']['value']

        if 'plain_text_input-action_2' in value:
            employee_data['last_name'] = value['plain_text_input-action_2']['value']
            employee_data['full_name'] = employee_data['first_name'] + ' ' + employee_data['last_name']

        if 'plain_text_input-action_3' in value:
            employee_data['address'] = value['plain_text_input-action_3']['value']

        if 'number_input-action_1' in value:
            if 'value' in value['number_input-action_1'] and value['number_input-action_1']['value'] is not None:
                employee_data['phone_number'] = value['number_input-action_1']['value']
            else:
                employee_data['phone_number'] = None

        if 'email_text_input-action_1' in value:
            employee_data['email_address'] = value['email_text_input-action_1']['value']

        if 'datepicker-action' in value:
            employee_data['joining_date'] = value['datepicker-action']['selected_date']

        if 'plain_text_input-action_4' in value:
            employee_data['job_level'] = value['plain_text_input-action_4']['value']

        if 'static_select-action_1' in value:
            employee_data['is_remote_employee'] = value['static_select-action_1']['selected_option']['value']

        if 'plain_text_input-action_5' in value:
            employee_data['designation'] = value['plain_text_input-action_5']['value']

        if 'plain_text_input-action_6' in value:
            skills = value['plain_text_input-action_6']['value']
            if skills:
                skill_data = [skill.strip() for skill in skills.split(",") if skill.strip()]
            else:
                skill_data = []
    return employee_data, skill_data, slack_user_id


def save_employee_details(employee_data, skill_data, slack_user_id):
    conn = get_postgres_conn()
    employee_id = insert_employee(conn, employee_data, slack_user_id)
    if skill_data:
        for skill in skill_data:
            skill = skill.lower()

            if not skill_exists(conn, skill):
                skill_id = insert_skill(conn, skill)
                thread = threading.Thread(target=get_skill_description_and_save_embedding, args=(skill, skill_id,))
                thread.start()
                link_skill_to_employee(conn, employee_id, skill_id)
                logging.info("Skill successfully saved and linked to employee")
            else:
                skill_id = get_skill_id_by_name(conn, skill)
                if not skill_embedding_exists(conn, skill_id):
                    thread = threading.Thread(target=get_skill_description_and_save_embedding, args=(skill, skill_id,))
                    thread.start()
                if not is_skill_linked(conn, employee_id, skill_id):
                    link_skill_to_employee(conn, employee_id, skill_id)
                    logging.info("Skill successfully linked to employee")
                else:
                    logging.info("Skill already linked to employee")

# Main function
def save_user_info(body):
    employee_data, skill_data, slack_user_id = parse_user_info(body)
    save_employee_details(employee_data, skill_data, slack_user_id)
    save_employee_embedding(employee_data, slack_user_id)
    return employee_data, skill_data

def get_skill_description_and_save_embedding(skill, skill_id):
    skill_desc = get_skill_description(skill)
    save_skill_embedding(skill_id, skill_desc)

def add_skill(body):
    skill_data = []
    slack_user_id = body['user']['id']
    for key, value in body['view']['state']['values'].items():
        if 'plain_text_input-action_6' in value:
            skills = value['plain_text_input-action_6']['value']
            skill_data = [skill.strip() for skill in skills.split(",") if skill.strip()]
            

    conn = get_postgres_conn()
    cursor = conn.cursor()
    employee_id = get_employee_id(conn, slack_user_id)
    logging.info("employee_id:", employee_id)

    for skill in skill_data:
        skill = skill.lower()
        if not skill_exists(conn, skill):
            skill_id = insert_skill(conn, skill)
            thread = threading.Thread(target=get_skill_description_and_save_embedding, args=(skill, skill_id,))
            thread.start()
            link_skill_to_employee(conn, employee_id, skill_id)
            logging.info("Skill successfully saved and linked to employee")
        else:
            skill_id = get_skill_id_by_name(conn, skill)
            if not skill_embedding_exists(conn, skill_id):
                thread = threading.Thread(target=get_skill_description_and_save_embedding, args=(skill, skill_id,))
                thread.start()
            if not is_skill_linked(conn, employee_id, skill_id):
                link_skill_to_employee(conn, employee_id, skill_id)
                logging.info("Skill successfully linked to employee")
            else:
                logging.info("Skill already linked to employee")
    skill_data = ', '.join(skill_data)
    return skill_data


def delete_skill(body):
    skill_data = []
    slack_user_id = body['user']['id']
    for key, value in body['view']['state']['values'].items():
        if 'plain_text_input-action_6' in value:
            skills = value['plain_text_input-action_6']['value']
            skill_data = [skill.strip() for skill in skills.split(",") if skill.strip()]

    conn = get_postgres_conn()
    cursor = conn.cursor()
    employee_id = get_employee_id(conn, slack_user_id)

    for skill in skill_data:
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
    skill_data = ', '.join(skill_data)
    return skill_data

