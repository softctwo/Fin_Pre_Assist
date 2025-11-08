"""向量化服务 - ChromaDB集成"""

import hashlib
from typing import List, Dict, Optional

import chromadb
import numpy as np
from chromadb.config import Settings
from loguru import logger

from app.core.config import settings
from app.models import DocumentType


class VectorService:
    """向量数据库服务"""

    def __init__(self):
        """初始化ChromaDB客户端"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY, settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )

        # 创建或获取集合
        self.documents_collection = self._get_or_create_collection("documents")
        self.knowledge_collection = self._get_or_create_collection("knowledge")
        self.proposals_collection = self._get_or_create_collection("proposals")

    def _get_or_create_collection(self, name: str):
        """获取或创建集合"""
        try:
            return self.client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        except Exception as e:
            logger.error(f"创建集合 {name} 失败: {e}")
            raise

    def _generate_id(self, content: str, prefix: str = "") -> str:
        """生成唯一ID，使用SHA-256哈希（更安全的哈希算法）"""
        if isinstance(content, list):
            content = "".join(str(item) for item in content)
        hash_obj = hashlib.sha256(content.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"

    def add_document(
        self,
        doc_id: int,
        title: str,
        content: str,
        metadata: Optional[Dict] = None,
        embedding: Optional[List[float]] = None,
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
            embeddings = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{vector_id}_chunk_{i}"
                ids.append(chunk_id)
                documents.append(chunk)

                chunk_metadata = {
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "vector_group_id": vector_id,
                    **(metadata or {}),
                }
                metadatas.append(chunk_metadata)
                if embedding:
                    embeddings.append(embedding)

            if embeddings:
                self.documents_collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
            else:
                self.documents_collection.add(ids=ids, documents=documents, metadatas=metadatas)

            logger.info(f"文档 {doc_id} 已添加到向量数据库，共 {len(chunks)} 个块")
            return vector_id

        except Exception as e:
            logger.error(f"添加文档到向量数据库失败: {e}")
            raise

    def batch_add_documents(self, documents: List[Dict]):
        """批量添加文档"""
        if not documents:
            return

        ids = []
        docs = []
        metadatas = []
        embeddings = []

        for doc in documents:
            doc_id = doc.get("doc_id")
            title = doc.get("title")
            content = doc.get("content")
            metadata = doc.get("metadata")
            embedding = doc.get("embedding")

            vector_id = self._generate_id(content, f"doc_{doc_id}")
            chunks = self._split_text(content, max_length=1000)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{vector_id}_chunk_{i}"
                ids.append(chunk_id)
                docs.append(chunk)

                chunk_metadata = {
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "vector_group_id": vector_id,
                    **(metadata or {}),
                }
                metadatas.append(chunk_metadata)
                if embedding:
                    embeddings.append(embedding)

        if embeddings:
            self.documents_collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)
        else:
            self.documents_collection.add(ids=ids, documents=docs, metadatas=metadatas)

    def add_knowledge(
        self, knowledge_id: int, title: str, content: str, category: str, metadata: Optional[Dict] = None
    ) -> str:
        """添加知识库条目到向量数据库"""
        try:
            vector_id = self._generate_id(content, f"kb_{knowledge_id}")

            self.knowledge_collection.add(
                ids=[vector_id],
                documents=[content],
                metadatas=[{"knowledge_id": knowledge_id, "title": title, "category": category, **(metadata or {})}],
            )

            logger.info(f"知识库条目 {knowledge_id} 已添加到向量数据库")
            return vector_id

        except Exception as e:
            logger.error(f"添加知识库到向量数据库失败: {e}")
            raise

    def upsert_knowledge(
        self, id: str, content: str, category: str, title: str, metadata: Optional[Dict] = None
    ) -> str:
        """更新或插入知识库条目"""
        try:
            vector_id = self._generate_id(content, f"kb_{id}")
            self.knowledge_collection.upsert(
                ids=[vector_id],
                documents=[content],
                metadatas=[{"knowledge_id": id, "title": title, "category": category, **(metadata or {})}],
            )
            logger.info(f"知识库条目 {id} 已更新/插入")
            return vector_id
        except Exception as e:
            logger.error(f"更新/插入知识库失败: {e}")
            raise

    def vectorize_proposal(
        self, proposal_id: str, requirements: str, content: str, metadata: Optional[Dict] = None
    ) -> str:
        """向量化方案"""
        try:
            vector_id = self._generate_id(content, f"proposal_{proposal_id}")
            self.proposals_collection.add(
                ids=[vector_id],
                documents=[content],
                metadatas=[{"proposal_id": proposal_id, "requirements": requirements, **(metadata or {})}],
            )
            logger.info(f"方案 {proposal_id} 已向量化")
            return vector_id
        except Exception as e:
            logger.error(f"向量化方案失败: {e}")
            raise

    def search_documents(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """搜索相似文档"""
        try:
            results = self.documents_collection.query(query_texts=[query], n_results=n_results, where=filter_metadata)

            return self._format_results(results)

        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            raise

    def search_knowledge(self, query: str, n_results: int = 5, category: Optional[str] = None) -> List[Dict]:
        """搜索知识库"""
        try:
            where_filter = {"category": category} if category else None

            results = self.knowledge_collection.query(query_texts=[query], n_results=n_results, where=where_filter)

            return self._format_results(results)

        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            raise

    def search_similar_proposals(self, requirements: str, n_results: int = 3) -> List[Dict]:
        """搜索相似的历史方案"""
        try:
            proposal_types = [
                DocumentType.TECHNICAL_PROPOSAL.value,
                DocumentType.BUSINESS_PROPOSAL.value,
                DocumentType.BID_DOCUMENT.value,
            ]

            doc_results = self.search_documents(
                query=requirements, n_results=n_results, filter_metadata={"type": {"$in": proposal_types}}
            )

            return doc_results

        except Exception as e:
            logger.error(f"搜索相似方案失败: {e}")
            raise

    def delete_document(self, vector_id: Optional[str], doc_id: Optional[int] = None) -> bool:
        """删除文档向量"""
        try:
            target_doc_id = doc_id or self._extract_doc_id(vector_id)

            if target_doc_id is not None:
                self.documents_collection.delete(where={"doc_id": target_doc_id})
                logger.info(f"文档 {target_doc_id} 的向量已删除")
                return True

            if vector_id:
                self.documents_collection.delete(where={"vector_group_id": vector_id})
                logger.info(f"文档向量组 {vector_id} 已删除")
                return True

            logger.warning("删除文档向量失败：缺少有效的 doc_id 或 vector_id")
            return False

        except Exception as e:
            logger.error(f"删除文档向量失败: {e}")
            return False

    def _extract_doc_id(self, vector_id: Optional[str]) -> Optional[int]:
        """从vector_id解析doc_id"""
        if not vector_id:
            return None
        try:
            parts = vector_id.split("_", 2)
            if len(parts) >= 2 and parts[0] == "doc":
                return int(parts[1])
        except ValueError:
            return None
        return None

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
        sentences = text.split("。")  # 按句子分割
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

        if not results["ids"] or not results["ids"][0]:
            return formatted

        for i, doc_id in enumerate(results["ids"][0]):
            formatted.append(
                {
                    "id": doc_id,
                    "document": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                }
            )

        return formatted

    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        return {
            "documents": self.documents_collection.count(),
            "knowledge": self.knowledge_collection.count(),
            "proposals": self.proposals_collection.count(),
        }

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """计算欧几里得距离"""
        return np.linalg.norm(np.array(vec1) - np.array(vec2))

    def _normalize_vector(self, vec: List[float]) -> List[float]:
        """归一化向量"""
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return (np.array(vec) / norm).tolist()


# 全局实例
vector_service = VectorService()
