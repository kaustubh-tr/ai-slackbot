# ai-slackbot

**ai-slackbot** is a custom Slack bot designed to interact with users using Slack slash commands and modals to manage user information and handle document-related queries. This bot is integrated with PostgreSQL and leverages language model chains for generating responses. Additionally, it supports embedding documents for advanced query processing and managing user skills.

The bot plays a key role in assisting users in their learning journey. It helps users by providing details of individuals from whom they can learn specific skills. If a user does not have the exact skill, the bot suggests a person with the most similar skill. When no individual matches, it offers relevant resources and links. Furthermore, it is designed to answer questions related to company policies and uploaded documents.

## Features

- **Save User Information:** Capture and store user details using Slack's modal feature.
- **Manage User Skills:** Add or remove user skills through easy-to-use Slack commands.
- **Document Embedding & Querying:** Process documents to generate embeddings and respond to document-related queries within Slack.
- **Interactive Slack Modals:** Provides a rich interactive experience through modals for user input.
- **Question-Answering System:** A conversational interface that responds to user queries based on pre-embedded knowledge.

## Prerequisites

Before starting, ensure the following:

1. **Slack Account & Workspace**: Create a Slack account and a workspace to install and interact with the bot.
2. **Python 3.x**: Installed on your local environment.
3. **PostgreSQL Database**: Set up a PostgreSQL instance for data storage.
4. **OpenAI/Cohere API Key**: These keys are required for generating responses and embeddings.
5. **LangChain & Slack Bolt**: The bot uses these libraries for language processing and Slack integration.

## Slack App Configuration

To configure and deploy the Slack bot, follow these steps:

### Step 1: Create a Slack App
1. Visit [Slack API Apps](https://api.slack.com/apps) and click **Create New App**.
2. Select **From scratch**, give your app a name, and choose your workspace.
3. Complete the app creation.

### Step 2: Set Up App Credentials
1. Under **Basic Information**:
   - In **App Credentials**, note down the **Signing Secret** as `SIGNING_SECRET`.
   - In **App-Level Token**, generate a token with the `connections:write` scope and note it as `SLACK_APP_TOKEN`.
2. Enable **Socket Mode** in the **Socket Mode** section.

### Step 3: Obtain Bot OAuth Token
1. Go to **Install App** and note the **Bot User OAuth Token** as `SLACK_BOT_TOKEN`.

### Step 4: Add Slash Commands
Define the following commands under **Slash Commands**:
- `/save-user-info`
- `/delete-user-skill`
- `/add-user-skill`
- `/add-document-query`

These commands interact with Slack modals for user input and data processing.

### Step 5: Set OAuth Scopes
In **OAuth & Permissions**, add these scopes:
- `app_mentions:read`, `channels:history`, `channels:read`, `chat:write`, `commands`, `im:history`, `im:write`, `users.profile:read`, `users:read`, `users:read.email`.

### Step 6: Reinstall App
Whenever changes are made, reinstall the app under the **Install App** section.

## Environment Variables

Configure environment variables in a `.env` file:

```env
# API Keys
OPENAI_API_KEY=<your_openai_api_key>
COHERE_API_KEY=<your_cohere_api_key>

# PostgreSQL Database Credentials
DB_USER=<your_db_username>
DB_PASS=<your_db_password>
DB_HOST=<your_db_host>
DB_PORT=<your_db_port>
DB_NAME=<your_db_name>

# Slack App Credentials
SLACK_BOT_TOKEN=<your_slack_bot_token>
SIGNING_SECRET=<your_signing_secret>
SLACK_APP_TOKEN=<your_slack_app_token>

# Postgres Vector URL for Embedding Storage
PG_VECTOR_URL=postgresql+psycopg2://<username>:<password>@localhost:<port>/<database>

# Document Base Directory
BASE_DIR=<your_base_directory_of_documents>
```

## Installation

Clone this repository and install the dependencies:

```bash
git clone https://github.com/your-username/ai-slackbot.git
cd ai-slackbot
pip install -r requirements.txt
```

Make sure to set up your `.env` file as outlined above.

## Running the Bot

To start the bot, simply run:

```bash
python app.py
```

This command will launch the bot using the Slack API's Socket Mode.

## Commands & Modal Usage

### `/add-document-query`
This command processes documents by generating embeddings and allows for document-based queries.

### `/save-user-info`
Presents a modal for saving user information like name, role, etc.

### `/add-user-skill`
Presents a modal to add specific skills for the user.

### `/delete-user-skill`
Presents a modal to delete skills previously added by the user.

## Useful Resources

- **LangChain Documentation**: [Introduction](https://python.langchain.com/v0.2/docs/
- **Slack Modals**: [Slack Modals Documentation](https://api.slack.com/surfaces/modals)
introduction/)
- **Block Kit Builder**: [Try Block Kit Builder](https://app.slack.com/block-kit-builder/)
- **Python Bolt**: [Bolt for Python](https://slack.dev/bolt-python/)

## Contributing

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Open a pull request.
