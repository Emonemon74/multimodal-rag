import os


from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from app.models.request_models import (
    QuestionRequest
)

from app.services.pdf_parser import (
    parse_pdf
)

from app.services.vector_store import (
    create_vector_store,
    load_vector_store
)

from app.services.llm import (
    generate_answer
)

router = APIRouter()


@router.post("/parse-pdf")
async def parse_pdf_api(
    file: UploadFile = File(...)
):

    # CREATE TEMP FOLDER
    os.makedirs(
        "temp",
        exist_ok=True
    )

    # FILE PATH
    file_location = (
        f"temp/{file.filename}"
    )

    # SAVE PDF
    with open(
        file_location,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )

    # PARSE PDF
    parsed_data = parse_pdf(
        file_location
    )

    # CREATE VECTOR DB
    create_vector_store(
        parsed_data["documents"]
    )

    return {
        "message":
        "PDF uploaded successfully"
    }


@router.post("/ask")
def ask_question(request: QuestionRequest):

    vector_store = load_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 6,
            "fetch_k": 20
        }
    )

    docs = retriever.invoke(request.question)

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    answer = generate_answer(
        request.question,
        context
    )

    return {
        "answer": answer
    }
