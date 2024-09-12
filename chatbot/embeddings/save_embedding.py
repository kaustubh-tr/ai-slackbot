import os
import psycopg2
from ..others import get_embedding
from ..database_utils.read_operation import get_postgres_conn, get_employee_id


def save_employee_embedding(employee_data, slack_user_id):
    conn = get_postgres_conn()
    cursor = conn.cursor()
    name = employee_data['full_name']
    embeddings = get_embedding(name.lower())
    employee_id = get_employee_id(conn, slack_user_id)
    query = f"""
        INSERT INTO botservice_empembedding (employee_id_id, embedding) VALUES ('{employee_id}', '{embeddings}')
        ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;"""
    cursor.execute(query)
    conn.commit()

def save_skill_embedding(skill_id, description):
    conn = get_postgres_conn()
    cursor = conn.cursor()
    embeddings = get_embedding(description)
    query = f"""
        INSERT INTO botservice_skillembedding (skill_id_id, description, embedding) VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;"""
    values = (skill_id, description, embeddings)
    cursor.execute(query, values)
    conn.commit()