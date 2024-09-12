import os
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
from .check_operation import employee_exists
from .read_operation import get_employee_id, get_skill_id_by_name

def insert_employee(conn, employee_data, slack_user_id):
    if not employee_exists(conn, slack_user_id):
        insert_employee_query = f"""
            INSERT INTO botservice_employee (slack_user_id, {', '.join(employee_data.keys())})
            VALUES ('{slack_user_id}', {', '.join(repr(value) if value is not None else 'NULL' for value in employee_data.values())})
        """
        cursor = conn.cursor()
        cursor.execute(insert_employee_query)
    else:
        update_employee_query = f"""
            UPDATE botservice_employee
            SET {(" , ".join( [ f"{key} = {repr(value)}" for key,value in employee_data.items() if value != None ] ))}
            WHERE slack_user_id = '{slack_user_id}'
        """
        cursor = conn.cursor()
        cursor.execute(update_employee_query)
    conn.commit()
    employee_id = get_employee_id(conn, slack_user_id)
    return employee_id


def insert_skill(conn, skill):
    insert_skill_query = f"INSERT INTO botservice_skill (skill_name) VALUES ('{skill}') RETURNING id"
    cursor = conn.cursor()
    cursor.execute(insert_skill_query)
    conn.commit()
    new_skill_id = get_skill_id_by_name(conn, skill)
    return new_skill_id

def link_skill_to_employee(conn, employee_id, skill_id):
    link_skill_query = f"INSERT INTO botservice_empskill (employee_id_id, skill_id_id) VALUES ('{employee_id}', '{skill_id}')"
    cursor = conn.cursor()
    cursor.execute(link_skill_query)
    conn.commit()