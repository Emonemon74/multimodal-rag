from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


PERSIST_DIRECTORY = "data/chroma_db"
COLLECTION_NAME = "pdf_chunks"

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")


def create_vector_store(records):

    documents = [
        Document(page_content=record["text"], metadata=record["metadata"])
        for record in records
    ]

    print("TOTAL DOCUMENTS:", len(documents))

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding_model,
    )

    vector_store.add_documents(documents)

    return vector_store


def load_vector_store():

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding_model,
    )
