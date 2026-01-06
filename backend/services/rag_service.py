from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_groq import ChatGroq
from typing import List, Tuple
from ..services.chat_service import get_history
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


# Build prompt
def create_prompt(question: str, chat_history: List[Tuple[str, str]], system_prompt: str):
    formatted_history = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_history if a is not None])

    template = f"""
    System: {system_prompt}
    Chat History:
    {formatted_history}

    User Input: {question}
    Answer concisely and informatively:
    """
    return PromptTemplate(
        input_variables=["chat_history", "question", "context"],
        template=template
    )


# RAG query
def query_rag(
        question: str,
        user_id: int,
        llm,
        session_id: str,
        system_prompt: str,
        memory_k: int = MEMORY_K
):
    chat_history = get_history(session_id)

    retriever = get_retriever(user_id)
    memory = ConversationBufferWindowMemory(k=memory_k, memory_key="chat_history", return_messages=True)
    prompt = create_prompt(question, chat_history, system_prompt)

    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt, "document_variable_name": "context"},
        output_key="answer",
        get_chat_history=lambda h: h
    )

    result = conv_chain({"question": question, "chat_history": chat_history})
    answer = result["answer"].strip()
    return answer
