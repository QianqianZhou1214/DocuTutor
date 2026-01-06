from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from langchain_groq import ChatGroq
from sqlalchemy.orm import Session
from .db_memory import load_memory_from_db
from ..services.embedding_factory import EmbeddingFactory

# settings
CHROMA_DIR = "./chroma_db"
MEMORY_K = 10


# Initializing LLM
def init_llm(groq_api_key: str, model_name: str = "llama3-8b-8192", temperature: float = 0.3, max_tokens: int = None):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )


# Initializing retriever
def get_retriever(user_id: int):
    embedding_function = EmbeddingFactory.create()
    return Chroma(
        collection_name=f"user_{user_id}",
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_function
    ).as_retriever(search_type="similarity", search_kwargs={"k": 4})


# RAG query
def query_rag(
        *,
        question: str,
        user_id: int,
        llm,
        session_id: str,
        db: Session,
        system_prompt: str,
) -> str:
    # load memory from DB
    memory = load_memory_from_db(db, session_id)
    # Retriever
    retriever = get_retriever(user_id)

    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        output_key="answer",
    )

    result = conv_chain({"question": question})
    answer = result["answer"].strip()
    return answer
