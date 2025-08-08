# src/rag.py

import fitz, asyncio
from io import BytesIO
from typing import List, Dict, Any

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter # <-- Use this instead of SemanticChunker
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from openai import AuthenticationError

from .config import settings

# get_rag_components is unchanged
def get_rag_components(api_key: str | None) -> Dict[str, Any]:
    """Dynamically selects the AI provider."""
    if api_key and api_key.startswith("sk-"):
        try:
            embeddings = OpenAIEmbeddings(api_key=api_key); llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.0, api_key=api_key); embeddings.embed_query("test")
            return {"embeddings": embeddings, "llm": llm}
        except (AuthenticationError, Exception):
            print("INFO: Falling back to Google/Gemini.")
    
    return {
        "embeddings": GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY),
        "llm": ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=settings.GOOGLE_API_KEY),
    }

async def process_document_and_answer(pdf_bytes: bytes, questions: List[str], api_key: str | None) -> List[str]:
    """
    Highly accurate and fast pipeline using a Multi-Query Retriever with a local FAISS index.
    """
    # 1. Get AI components
    components = get_rag_components(api_key)
    embeddings = components["embeddings"]
    llm = components["llm"]

    # 2. Extract Text and Perform FAST Character Chunking
    print("INFO: Extracting text and performing fast character-based chunking...")
    text = "".join(page.get_text() for page in fitz.open(stream=pdf_bytes, filetype="pdf"))
    
    # --- CHUNKING STRATEGY UPDATED FOR SPEED ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # Large overlap helps maintain context
        length_function=len
    )
    chunks_text = text_splitter.split_text(text)
    
    if not chunks_text:
        raise ValueError("No text could be extracted or chunked from the document.")
    print(f"INFO: Document split into {len(chunks_text)} chunks.")

    # 3. Create a local FAISS index IN MEMORY
    print("INFO: Creating local FAISS index in memory...")
    vectorstore = await FAISS.afrom_texts(texts=chunks_text, embedding=embeddings)
    
    # 4. Create the ADVANCED Multi-Query Retriever
    print("INFO: Setting up Multi-Query Retriever...")
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 7})
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )
    print("INFO: Advanced retriever is ready.")

    # 5. Define prompt and chain
    template = """You are an expert assistant who makes complicated documents easy to understand.
Your task is to answer the following question using *only* the provided context.

First, think step-by-step to analyze the user's question and the context.
1.  Identify the key entities and concepts in the question.
2.  Scan the context and locate the parts that are directly relevant to these key concepts.
3.  Synthesize the relevant information from the context into a single, cohesive answer.

After your step-by-step analysis, provide the final answer in simple English, following these rules:
- **Be Direct and Precise:** Answer the question directly without adding extra information.
- **Stay Brief:** Keep your answer as short as possible.
- **Use Only the Context:** If the answer is not in the text below, you must reply with: "I could not find the answer to that question in the document."

---
CONTEXT:
{context}
---

QUESTION:
{question}

---
FINAL ANSWER IN SIMPLE ENGLISH:"""
    prompt = PromptTemplate.from_template(template)
    
    chain = {"context": multi_query_retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

    # 6. Generate answers in parallel
    print("INFO: Generating answers for all questions in parallel...")
    answers = await chain.abatch(questions, {"max_concurrency": 10})
    print("INFO: All questions answered.")
    return answers