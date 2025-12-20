import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. API 키 설정 (환경 변수 사용)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

def run_lcel_rag():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_api_key,
        temperature=0
    )
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=gemini_api_key
    )

    # 3. 문서 로드 및 분할
    file_path = "document.pdf"
    if not os.path.exists(file_path):
        print(f"'{file_path}' 파일이 없습니다.")
        return

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # 4. 벡터 스토어 및 리트리버 설정
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    # 5. 프롬프트 템플릿 정의
    template = """다음 제공된 컨텍스트를 사용하여 질문에 답하세요. 
    답을 모른다면 모른다고 답변하고 지어내지 마세요.
    답변은 3문장 이내로 간결하게 작성하세요.

    컨텍스트: {context}

    질문: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 6. LCEL 체인 구성 (핵심 부분)
    # 헬퍼 함수: 검색된 문서들을 하나의 텍스트로 합쳐줍니다.
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 7. 실행
    query = "이 문서의 주요 내용을 요약해줘."
    print(f"\n질문: {query}")
    
    # LCEL 방식에서는 딕셔너리가 아닌 질문 문자열만 넘겨도 작동합니다.
    response = rag_chain.invoke(query)
    print(f"\n답변:\n{response}")

if __name__ == "__main__":
    run_lcel_rag()