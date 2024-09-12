GET_EMPLOYEE_BY_SKILL_QUERY=''' 
    SELECT e."first_name", e."last_name", e."is_remote_employee", s."skill_name", e."job_level", e."designation", e."job_description"
    FROM botservice_empskill es
    JOIN botservice_employee e ON es."employee_id_id" = e."id"
    JOIN botservice_skill s ON es."skill_id_id" = s."id"
    WHERE LOWER(s."skill_name") = LOWER('{skill}')
    AND e."id" != '{employee_id}'
    LIMIT 3;
    '''

GET_SKILL_BY_EMPLOYEE_QUERY=''' 
    SELECT e."first_name", e."last_name", e."is_remote_employee", e."job_level", e."designation", e."job_description", s."skill_name"
    FROM botservice_employee e
    LEFT JOIN botservice_empskill es ON e."id" = es."employee_id_id"
    LEFT JOIN botservice_skill s ON es."skill_id_id" = s."id"
    WHERE LOWER(e."first_name") = LOWER('{name}')
    OR LOWER(e."last_name") = LOWER('{name}')
    OR LOWER(e."full_name") = LOWER('{name}')
    '''

GET_SKILL_BY_MY_NAME_QUERY=''' 
    SELECT e."first_name", e."last_name", e."is_remote_employee", e."job_level", e."designation", e."job_description", s."skill_name"
    FROM botservice_employee e
    LEFT JOIN botservice_empskill es ON e."id" = es."employee_id_id"
    LEFT JOIN botservice_skill s ON es."skill_id_id" = s."id"
    WHERE e."id" = '{name}'
    '''

SKILL_EXISTS_QUERY='''
    SELECT EXISTS(
        SELECT 1 
        FROM botservice_skill s
        JOIN botservice_empskill es ON s.id = es.skill_id_id
        WHERE LOWER(s."skill_name") = LOWER('{skill}')
    )
    '''

EMPLOYEE_EXISTS_QUERY='''
    SELECT EXISTS(
        SELECT 1
        FROM botservice_employee e
        WHERE LOWER(e."full_name") = LOWER('{name}')
    )
    '''

GET_EMPLOYEE_BY_EMBEDDING = '''
    SELECT e.full_name, subquery.employee_id_id, subquery.cosine_similarity
    FROM (
        SELECT ee.employee_id_id, 1-(embedding <=> '{name_embedding}') AS cosine_similarity
        FROM botservice_empembedding ee
    ) AS subquery
    JOIN botservice_employee e ON subquery.employee_id_id = e.id
    WHERE subquery.cosine_similarity > {threshold}
    ORDER BY subquery.cosine_similarity DESC
    LIMIT 1;
    '''

GET_SKILL_BY_EMBEDDING = '''
    SELECT s.skill_name, subquery.skill_id_id, subquery.cosine_similarity
    FROM (
        SELECT se.skill_id_id, 1-(embedding <=> '{skill_embedding}') AS cosine_similarity
        FROM botservice_skillembedding se
    ) AS subquery
    JOIN botservice_skill s ON subquery.skill_id_id = s.id
    WHERE subquery.cosine_similarity > {threshold}
    ORDER BY subquery.cosine_similarity DESC
    LIMIT 5;
    '''

GET_SKILL_EMBEDDING_QUERY = '''
    SELECT se.embedding
    FROM botservice_skillembedding se
    JOIN botservice_skill s ON se.skill_id_id = s.id
    WHERE s.skill_name = '{skill}';
    '''

GET_CHAT_HISTORY_QUERY = '''
    SELECT *
    FROM (
        SELECT *
        FROM botservice_chathistory
        WHERE employee_id_id = '{employee_id}'
        ORDER BY timestamp DESC
        LIMIT 10
    ) AS last_10_chats
    ORDER BY timestamp ASC;
    '''

GET_USER_SKILL_QUERY = '''
    SELECT s."skill_name"
    FROM botservice_empskill es
    JOIN botservice_skill s ON es."skill_id_id" = s."id"
    WHERE es."employee_id_id" = '{employee_id}';
    '''