import os
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
import pandas as pd
from datetime import datetime
from ..queries import GET_CHAT_HISTORY_QUERY, GET_SKILL_BY_MY_NAME_QUERY, GET_USER_SKILL_QUERY

def get_postgres_conn():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        logging.info("Connected to PostgreSQL!")
        return conn

    except psycopg2.Error as e:
        logging.error("Unable to connect to PostgreSQL:", e)
        return None

def get_chat_history(employee_id):
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        query = GET_CHAT_HISTORY_QUERY.format(employee_id=employee_id)
        cursor.execute(query)
        chat_history = cursor.fetchall()
        conn.close()
        return chat_history

    except Exception as e:
        logging.error("An error occurred, get_chat_history:", e)
        return None

def get_stored_skills():
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT LOWER(s."skill_name") FROM botservice_skill s ;""")
        stored_skills = [row[0] for row in cursor.fetchall()]
        return stored_skills

    except Exception as e:
        logging.error("An error occurred, get_stored_skills:", e)
        return None

def get_employees_name():
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT LOWER(e."full_name") FROM botservice_employee e ;""")
        employees_name = [row[0] for row in cursor.fetchall()]
        return employees_name

    except Exception as e:
        logging.error("An error occurred, get_employees_name:", e)
        return None

def get_slack_user_ids():
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT LOWER(e."slack_user_id") FROM botservice_employee e ;""")
        slack_user_ids = [row[0] for row in cursor.fetchall()]
        return slack_user_ids

    except Exception as e:
        logging.error("An error occurred, get_slack_user_ids:", e)
        return None

def get_user_info(employee_id):
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        query = GET_SKILL_BY_MY_NAME_QUERY.format(name=employee_id) ######
        cursor.execute(query)
        temp = pd.read_sql(query, conn)
        user_info = temp.to_dict(orient='records')
        return user_info

    except Exception as e:
        logging.error("An error occurred, find_most_similar_employee:", e)
        return None

def get_employee_id(conn, slack_user_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM botservice_employee WHERE slack_user_id = '{slack_user_id}'")
    row = cursor.fetchone()
    return row[0] if row else None

def get_skill_id_by_name(conn, skill):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM botservice_skill WHERE LOWER(skill_name) = ('{skill}')")
    row = cursor.fetchone()
    return row[0] if row else None

def get_user_skills(body):
    slack_user_id = body['user_id']
    conn = get_postgres_conn()
    cursor = conn.cursor()
    employee_id = get_employee_id(conn, slack_user_id)
    query = GET_USER_SKILL_QUERY.format(employee_id=employee_id)
    cursor.execute(query)
    user_skills = [row[0] for row in cursor.fetchall()]
    user_skills = ', '.join(user_skills)
    return user_skills