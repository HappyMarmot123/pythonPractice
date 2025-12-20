import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

class VectorResourceManager:
    def __init__(self, db_path: str = "data/db"):
        self.db_path = db_path
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        # 폴더가 없으면 생성
        os.makedirs(self.db_path, exist_ok=True)

    def create_or_get_vectorstore(self) -> Chroma:
        """
        기존 벡터 DB를 로드합니다.
        """
        vectorstore = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings
        )
        return vectorstore

    def get_retriever(self):
        """리트리버 객체 반환 (상위 k개 결과 설정 가능)"""
        vectorstore = self.create_or_get_vectorstore()
        return vectorstore.as_retriever(search_kwargs={"k": 3})

# 사용 예시 (테스트용)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    manager = VectorResourceManager()
    retriever = manager.get_retriever()  # 기존 DB 로드