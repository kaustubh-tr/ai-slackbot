import os
import re
import logging
import psycopg2
import threading
import time
logging.basicConfig(level=logging.DEBUG)
import langchain
langchain.debug=True
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from chatbot.main import SlackBot
from chatbot.database_utils.read_operation import get_postgres_conn
from chatbot.slack_integration import save_user_info, add_skill, delete_skill
from chatbot.embeddings.document_embedding import process_all_documents
from chatbot.database_utils.read_operation import get_employee_id, get_user_skills
from chatbot.modals import onboarding_view, add_skill_view, delete_skill_view

app = App(token=os.environ["SLACK_BOT_TOKEN"])
slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

def convert_to_markdown(text):
    pattern = r'\*\*([^*]+)\*\*'
    return re.sub(pattern, r'*\1*', text)


@app.event("app_mention")
def event_test(event, say):
    say(f"Hi there, <@{event['user']}>!")

def ack_command(ack):
    ack()

@app.command("/add-document-query")
def document_query(ack, respond, command, body, client):
    ack()
    process_all_documents()
    respond(f"Documents Successfully Processed!")

#################################

@app.command("/save-user-info")
def onboarding_modal(body, ack, respond, client, logger):
    logger.info(body)
    ack()
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view=onboarding_view(),
    )
    logger.info(res)

@app.view("view-id")
def submission(ack, body, client, logger):
    user = body["user"]["id"]
    try:
        save_user_info(body)
        ack()
        msg = "Your details submission was successful"
        client.chat_postMessage(channel=user, text=msg)

    except Exception as e:
        logger.exception(f"Failed to save user info or post message: {e}")
        ack()
        msg = "There was an error with your submission"
        try:
            client.chat_postMessage(channel=user, text=msg)

        except Exception as e:
            logger.exception(f"Failed to post a message: {e}")

#################################

@app.command("/add-user-skill")
def add_skill_modal(body, ack, respond, client, logger):
    logger.info(body)
    ack()
    user_skills = get_user_skills(body)
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view=add_skill_view(user_skills),
    )
    logger.info(res)

@app.view("view-id_1")
def submission(ack, body, client, logger):
    user = body["user"]["id"]
    skill_data = add_skill(body)
    ack()
    msg = ""
    try:
        msg = f"Your request to add skills: {skill_data} was successful"
    except Exception as e:
        msg = "There was an error with your submission"

    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")

#################################

@app.command("/delete-user-skill")
def delete_skill_modal(body, ack, respond, client, logger):
    logger.info(body)
    ack()
    user_skills = get_user_skills(body)
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view=delete_skill_view(user_skills),
    )
    logger.info(res)

@app.view("view-id_2")
def submission(ack, body, client, logger):
    user = body["user"]["id"]
    skill_data = delete_skill(body)
    ack()
    msg = ""
    try:
        msg = f"Your request to delete skills: {skill_data} was successful"
    except Exception as e:
        msg = "There was an error with your submission"
        
    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")

#################################

# Slack Event Handler
@app.message(re.compile(".*"))  # Match any text
def handle_event(body, ack, respond, client, logger, say, context):
    question = body['event']['text']
    bot_id = context['bot_user_id']
    slack_user_id = context['user_id']
    conn = get_postgres_conn()
    cursor = conn.cursor()
    employee_id = get_employee_id(conn, slack_user_id)
    chat_bot = SlackBot()
    answer = chat_bot.get_response(question, employee_id, bot_id)
    logging.info("\nanswer:", answer)
    if answer == "Sorry, I am unable to answer this question.":
        final_answer = answer
    elif answer == "It seems like I don't have any information about you. Please save your details by using the below command, so that I can provide you with personalized assistance: ```/save-user-info```":
        final_answer = answer
    else:
        final_answer = convert_to_markdown(answer['output'])
    say(final_answer)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()