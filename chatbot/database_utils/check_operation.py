import os
import psycopg2
from .read_operation import get_postgres_conn

def employee_exists(conn, slack_user_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM botservice_employee WHERE slack_user_id = '{slack_user_id}')")
    return cursor.fetchone()[0]

def skill_exists(conn, skill):
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM botservice_skill WHERE LOWER(skill_name) = LOWER('{skill}'))")
    return cursor.fetchone()[0]

def is_skill_linked(conn, employee_id, skill_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM botservice_empskill WHERE employee_id_id = '{employee_id}' AND skill_id_id = '{skill_id}')")
    return cursor.fetchone()[0]

def skill_embedding_exists(conn, skill_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM botservice_skillembedding WHERE skill_id_id = '{skill_id}')")
    return cursor.fetchone()[0]