import os
from dotenv import load_dotenv
load_dotenv()
MODEL_NAME="gpt-4o-mini"
# MODEL_NAME="gpt-4o"
COLLECTION_NAME="Company_Policies"
EMBEDDINGS_MODEL="text-embedding-3-small"
CONNECTION_STRING=os.getenv('PG_VECTOR_URL')
BASE_DIR=os.getenv('BASE_DIR')
RERANK_MODEL="rerank-english-v3.0"
