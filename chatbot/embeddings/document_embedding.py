import glob
import logging
logging.basicConfig(level=logging.DEBUG)
from langchain_community.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..constant import COLLECTION_NAME, CONNECTION_STRING, EMBEDDINGS_MODEL, BASE_DIR

class EmbeddingManager:
    def __init__(self):
        self.vector_db = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
            embedding_function=OpenAIEmbeddings(model=EMBEDDINGS_MODEL),
            distance_strategy=DistanceStrategy.COSINE,
        )

    def create_documents(self, file_path):
        pages = []
        loader = PyMuPDFLoader(file_path)
        pages.extend(loader.load_and_split())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        documents = text_splitter.split_documents(pages)
        return documents

    def store_embedding(self, documents):
        res = self.vector_db.add_documents(documents)
        return res

    
def process_all_documents():
    emb_manager = EmbeddingManager()
    pdf_files = glob.glob(f"{BASE_DIR}/**/*.pdf", recursive=True)
    
    for path in pdf_files:
        documents = emb_manager.create_documents(path)
        emb_manager.store_embedding(documents)
        logging.info(f"Processed {len(documents)} documents from {path}")