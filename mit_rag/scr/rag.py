import time
from typing import List, Tuple, Any
from .config import OLLAMA_HOST, MODEL_NAME, EMBEDDING_MODEL, PREFERRED_MODELS


def test_ollama_connection() -> Tuple[bool, str]:
    try:
        import requests

        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Normalize model names from response
            model_names = []
            for m in models:
                if isinstance(m, dict):
                    model_names.append(m.get("name") or m.get("id") or "")
                else:
                    model_names.append(str(m))

            # If configured MODEL_NAME exists, use it; otherwise pick from preferences
            selected = None
            if MODEL_NAME in model_names:
                selected = MODEL_NAME
            else:
                for pref in PREFERRED_MODELS:
                    if pref in model_names:
                        selected = pref
                        break

            if selected:
                return True, f"✅ Connected! Using model: {selected}"
            else:
                return (
                    False,
                    f"❌ None of preferred models found. Available: {model_names}",
                )
        else:
            return False, f"❌ Ollama error: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"


def load_doc(list_file_path: List[str]):
    # local import to avoid top-level dependency issues
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import PyPDFLoader
    except Exception as e:
        raise RuntimeError(
            "Missing langchain or document loader packages. Install requirements to use load_doc()"
        ) from e

    loaders = [PyPDFLoader(x) for x in list_file_path]
    pages = []
    for loader in loaders:
        pages.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    doc_splits = text_splitter.split_documents(pages)
    return doc_splits


def create_db(splits):
    try:
        # Import locally to avoid errors if not installed
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
    except Exception as e:
        raise RuntimeError(
            "Missing embedding/vectorstore packages. Install requirements to use create_db()"
        ) from e

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectordb = FAISS.from_documents(splits, embeddings)
    return vectordb


def initialize_chatbot(vector_db):
    connection_status, connection_message = test_ollama_connection()
    if not connection_status:
        raise Exception(f"Ollama connection failed: {connection_message}")

    try:
        from langchain.memory import ConversationBufferMemory

        # Import locally to avoid errors if not installed
        try:
            from langchain_ollama import OllamaLLM as Ollama
        except ImportError:
            from langchain_community.llms import Ollama
        from langchain.chains import ConversationalRetrievalChain
    except Exception as e:
        raise RuntimeError(
            "Missing langchain or Ollama integration packages. Install requirements to use initialize_chatbot()"
        ) from e

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vector_db.as_retriever()

    # Extract selected model from connection_message if available
    model_to_use = MODEL_NAME
    try:
        if "Using model:" in connection_message:
            model_to_use = connection_message.split("Using model:")[-1].strip()
    except Exception:
        pass

    llm = Ollama(model=model_to_use, base_url=OLLAMA_HOST, temperature=0.5)

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory, verbose=False
    )
    return qa_chain


def process_and_initialize(files: List[Any]):
    if not files:
        return None, None, "Please upload a file first."

    try:
        # Support both Gradio File objects (with .name) and filepath strings
        list_file_path = []
        for file in files:
            if file is None:
                continue
            # gr.Files(..., type="filepath") returns strings (paths)
            if isinstance(file, str):
                list_file_path.append(file)
            else:
                # file-like object that may have a 'name' attribute
                list_file_path.append(getattr(file, "name", str(file)))
        doc_splits = load_doc(list_file_path)
        db = create_db(doc_splits)
        qa = initialize_chatbot(db)
        return db, qa, "Database created! Ready for questions."
    except Exception as e:
        return None, None, f"Processing error: {str(e)}"


def user_query_typing_effect(query: str, qa_chain, chatbot):
    history = chatbot or []
    try:
        response = qa_chain.invoke({"question": query, "chat_history": []})
        assistant_response = response["answer"]
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": ""})
        for i in range(len(assistant_response)):
            history[-1]["content"] += assistant_response[i]
            yield history, ""
            time.sleep(0.03)
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        yield history, ""
