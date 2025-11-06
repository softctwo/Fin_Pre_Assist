"""向量化服务 - ChromaDB集成"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from loguru import logger
import hashlib

from app.core.config import settings


class VectorService:
    """向量数据库服务"""

    def __init__(self):
        """初始化ChromaDB客户端"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 创建或获取集合
        self.documents_collection = self._get_or_create_collection("documents")
        self.knowledge_collection = self._get_or_create_collection("knowledge")
        self.proposals_collection = self._get_or_create_collection("proposals")

    def _get_or_create_collection(self, name: str):
        """获取或创建集合"""
        try:
            return self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"创建集合 {name} 失败: {e}")
            raise

    def _generate_id(self, content: str, prefix: str = "") -> str:
        """生成唯一ID"""
        hash_obj = hashlib.md5(content.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"

    def add_document(
        self,
        doc_id: int,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """添加文档到向量数据库"""
        try:
            vector_id = self._generate_id(content, f"doc_{doc_id}")

            # 将文档分块（如果太长）
            chunks = self._split_text(content, max_length=1000)

            # 添加所有块到集合
            ids = []
            documents = []
            metadatas = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{vector_id}_chunk_{i}"
                ids.append(chunk_id)
                documents.append(chunk)

                chunk_metadata = {
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **(metadata or {})
                }
                metadatas.append(chunk_metadata)

            self.documents_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(f"文档 {doc_id} 已添加到向量数据库，共 {len(chunks)} 个块")
            return vector_id

        except Exception as e:
            logger.error(f"添加文档到向量数据库失败: {e}")
            raise

    def add_knowledge(
        self,
        knowledge_id: int,
        title: str,
        content: str,
        category: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """添加知识库条目到向量数据库"""
        try:
            vector_id = self._generate_id(content, f"kb_{knowledge_id}")

            self.knowledge_collection.add(
                ids=[vector_id],
                documents=[content],
                metadatas=[{
                    "knowledge_id": knowledge_id,
                    "title": title,
                    "category": category,
                    **(metadata or {})
                }]
            )

            logger.info(f"知识库条目 {knowledge_id} 已添加到向量数据库")
            return vector_id

        except Exception as e:
            logger.error(f"添加知识库到向量数据库失败: {e}")
            raise

    def search_documents(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """搜索相似文档"""
        try:
            results = self.documents_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )

            return self._format_results(results)

        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            raise

    def search_knowledge(
        self,
        query: str,
        n_results: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """搜索知识库"""
        try:
            where_filter = {"category": category} if category else None

            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )

            return self._format_results(results)

        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            raise

    def search_similar_proposals(
        self,
        requirements: str,
        n_results: int = 3
    ) -> List[Dict]:
        """搜索相似的历史方案"""
        try:
            # 先从文档集合中搜索
            doc_results = self.search_documents(
                query=requirements,
                n_results=n_results,
                filter_metadata={"type": "proposal"}
            )

            return doc_results

        except Exception as e:
            logger.error(f"搜索相似方案失败: {e}")
            raise

    def delete_document(self, vector_id: str) -> bool:
        """删除文档向量"""
        try:
            # 删除所有相关的块
            self.documents_collection.delete(
                where={"$contains": vector_id}
            )
            logger.info(f"文档向量 {vector_id} 已删除")
            return True

        except Exception as e:
            logger.error(f"删除文档向量失败: {e}")
            return False

    def delete_knowledge(self, vector_id: str) -> bool:
        """删除知识库向量"""
        try:
            self.knowledge_collection.delete(ids=[vector_id])
            logger.info(f"知识库向量 {vector_id} 已删除")
            return True

        except Exception as e:
            logger.error(f"删除知识库向量失败: {e}")
            return False

    def _split_text(self, text: str, max_length: int = 1000) -> List[str]:
        """将长文本分割成小块"""
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = text.split('。')  # 按句子分割
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "。"

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _format_results(self, results: Dict) -> List[Dict]:
        """格式化搜索结果"""
        formatted = []

        if not results['ids'] or not results['ids'][0]:
            return formatted

        for i, doc_id in enumerate(results['ids'][0]):
            formatted.append({
                'id': doc_id,
                'document': results['documents'][0][i] if results['documents'] else None,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else None,
            })

        return formatted

    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        return {
            'documents': self.documents_collection.count(),
            'knowledge': self.knowledge_collection.count(),
            'proposals': self.proposals_collection.count(),
        }


# 全局实例
vector_service = VectorService()
