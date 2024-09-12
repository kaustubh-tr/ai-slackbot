import os
import cohere
import logging
logging.basicConfig(level=logging.DEBUG)
from langchain.agents import Tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy
from ..templates import VECTOR_DB_DESC
from ..constant import COLLECTION_NAME, CONNECTION_STRING, EMBEDDINGS_MODEL, RERANK_MODEL
from langchain.tools import BaseTool, StructuredTool, tool
from dotenv import load_dotenv
load_dotenv()
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

vector_db = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=OpenAIEmbeddings(model=EMBEDDINGS_MODEL),
    distance_strategy=DistanceStrategy.COSINE,
)

def rerank_documents(query, documents, top_n=6):
    co = cohere.Client(COHERE_API_KEY)
    response = co.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=documents,
        top_n=top_n
    )
    reranked_documents = [documents[res.index] for res in response.results]
    return reranked_documents

def convert_doc_to_str(docs):
    return [
        f"Document {i+1}:\n\n" + "Source: " + d.metadata["source"] + "\n" + "Page: " + str(d.metadata["page"]) + "\n" + d.page_content
        for i, d in enumerate(docs)
    ]

# def get_retriever():
#     retriever = vector_db.as_retriever(search_kwargs={"k": 4})
#     return retriever

def get_docs(query):        
    try:
        docs = vector_db.similarity_search(query=query, k=15)
        formatted_docs = convert_doc_to_str(docs)
        top_ranked_docs = rerank_documents(query=query, documents=formatted_docs)
        return "\n".join(top_ranked_docs)

    except Exception as e:
        logging.error("An error occurred in get_docs", e)
        return "No document found."

# def vector_db_search(query: str = Field(description="should be a fully formed question.")):
#     result = vector_db.similarity_search(question)
#     res = f"\n{'-' * 100}\n".join(
#         [
#             f"Document {i+1}:\n\n" + "\n" + d.page_content
#             for i, d in enumerate(result)
#         ]
#     )
#     return res

def get_vector_db_search_tool(question):
    try:
        vector_db_search_tool = StructuredTool.from_function(
            name="DOCUMENT_VECTOR_DB_SEARCH",
            func=get_docs,
            description=VECTOR_DB_DESC,
        )
        return vector_db_search_tool
        
    except Exception as e:
        logging.error("An error occured, get_vector_db_search_tool:", e)
