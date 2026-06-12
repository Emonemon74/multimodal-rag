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


def search_pdf_chunks(query, k=6, fetch_k=20):

    vector_store = load_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr", search_kwargs={"k": k, "fetch_k": fetch_k}
    )

    docs = retriever.invoke(query)

    return [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "Unknown"),
            "chunk_index": doc.metadata.get("chunk_index", "Unknown"),
            "content": doc.page_content,
        }
        for doc in docs
    ]
