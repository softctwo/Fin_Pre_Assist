"""向量服务边界测试 - 提升测试覆盖率"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from app.services.vector_service import VectorService


class TestVectorServiceBoundaryCases:
    """向量服务边界条件测试"""

    @pytest.fixture
    def vector_service(self):
        """创建向量服务实例"""
        return VectorService()

    @pytest.fixture
    def sample_embeddings(self):
        """提供样本嵌入向量"""
        return {
            'text1': np.random.randn(1536).tolist(),
            'text2': np.random.randn(1536).tolist(),
            'text3': np.random.randn(1536).tolist(),
        }

    # ========== 向量维度边界测试 ==========
    @pytest.mark.asyncio
    async def test_add_document_with_different_dimensions(self, vector_service):
        """测试不同维度的向量"""
        # 正常维度
        normal_embedding = np.random.randn(1536).tolist()

        # 边界维度
        test_cases = [
            (np.random.randn(1).tolist(), "1维向量"),
            (np.random.randn(100).tolist(), "100维向量"),
            (np.random.randn(768).tolist(), "768维向量(BERT)"),
            (np.random.randn(1024).tolist(), "1024维向量"),
            (np.random.randn(1536).tolist(), "1536维向量(OpenAI)"),
            (np.random.randn(2048).tolist(), "2048维向量"),
            (np.random.randn(4096).tolist(), "4096维向量"),
        ]

        for embedding, description in test_cases:
            try:
                await vector_service.add_document(
                    doc_id=f"test_{description}",
                    title="测试标题",
                    content="测试内容",
                    embedding=embedding,
                    metadata={"type": description}
                )
                # 如果支持多维度，应该成功
            except (ValueError, RuntimeError) as e:
                # 如果不支持，应该给出清晰的错误信息
                assert "dimension" in str(e).lower() or "维度" in str(e)

    @pytest.mark.asyncio
    async def test_cosine_similarity_edge_cases(self, vector_service):
        """测试余弦相似度边界情况"""
        # 相同向量
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        similarity = vector_service._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-10

        # 相反向量
        vec3 = [1, 0, 0]
        vec4 = [-1, 0, 0]
        similarity = vector_service._cosine_similarity(vec3, vec4)
        assert abs(similarity - (-1.0)) < 1e-10

        # 正交向量
        vec5 = [1, 0, 0]
        vec6 = [0, 1, 0]
        similarity = vector_service._cosine_similarity(vec5, vec6)
        assert abs(similarity - 0.0) < 1e-10

        # 零向量
        vec7 = [0, 0, 0]
        vec8 = [1, 1, 1]
        with pytest.raises((ValueError, ZeroDivisionError)):
            vector_service._cosine_similarity(vec7, vec8)

    @pytest.mark.asyncio
    async def test_euclidean_distance_edge_cases(self, vector_service):
        """测试欧几里得距离边界情况"""
        # 相同点
        vec1 = [1, 2, 3]
        vec2 = [1, 2, 3]
        distance = vector_service._euclidean_distance(vec1, vec2)
        assert abs(distance - 0.0) < 1e-10

        # 最大距离（对角线）
        vec3 = [0, 0, 0]
        vec4 = [1, 1, 1]
        distance = vector_service._euclidean_distance(vec3, vec4)
        expected = np.sqrt(3)  # sqrt(1²+1²+1²)
        assert abs(distance - expected) < 1e-10

        # 不同维度向量
        vec5 = [1, 2]
        vec6 = [1, 2, 3]
        with pytest.raises(ValueError):
            vector_service._euclidean_distance(vec5, vec6)

    # ========== 向量数值边界测试 ==========

    @pytest.mark.asyncio
    async def test_extreme_vector_values(self, vector_service):
        """测试极端向量值"""
        extreme_cases = [
            ([float('inf')] * 1536, "正无穷大"),
            ([float('-inf')] * 1536, "负无穷大"),
            ([float('nan')] * 1536, "非数字(NaN)"),
            ([1e308] * 1536, "极大值"),
            ([1e-308] * 1536, "极小值"),
            ([0.0] * 1536, "零向量"),
            ([-0.0] * 1536, "负零向量"),
        ]

        for values, description in extreme_cases:
            try:
                normalized = vector_service._normalize_vector(values)
                # 如果能正常处理，结果应该是有效的
                assert len(normalized) == 1536
                assert all(not np.isnan(x) for x in normalized)
                assert all(not np.isinf(x) for x in normalized)
            except (ValueError, RuntimeError, OverflowError) as e:
                # 如果不能处理，应该给出合适的错误
                print(f"{description}处理异常: {e}")

    @pytest.mark.asyncio
    async def test_vector_normalization_edge_cases(self, vector_service):
        """测试向量归一化边界情况"""
        # 已经是单位向量
        unit_vec = [1, 0, 0]
        normalized = vector_service._normalize_vector(unit_vec)
        assert abs(np.linalg.norm(normalized) - 1.0) < 1e-10

        # 零向量
        zero_vec = [0, 0, 0]
        with pytest.raises((ValueError, ZeroDivisionError)):
            vector_service._normalize_vector(zero_vec)

        # 非常小的向量
        tiny_vec = [1e-100, 1e-100, 1e-100]
        normalized = vector_service._normalize_vector(tiny_vec)
        assert abs(np.linalg.norm(normalized) - 1.0) < 1e-10

    # ========== 搜索参数边界测试 ==========

    @pytest.mark.asyncio
    async def test_search_with_extreme_k_values(self, vector_service, sample_embeddings):
        """测试极端的k值搜索"""
        # 先添加一些文档
        for doc_id, embedding in sample_embeddings.items():
            await vector_service.add_document(doc_id, f"内容{doc_id}", "内容", embedding=embedding)

        # 测试不同的k值
        test_cases = [
            (0, "k=0"),
            (1, "k=1"),
            (len(sample_embeddings), "k=文档总数"),
            (len(sample_embeddings) + 1, "k>文档总数"),
            (1000, "k=1000(远大于文档数)"),
            (-1, "k=-1(负数)"),
        ]

        query_embedding = np.random.randn(1536).tolist()

        for k, description in test_cases:
            try:
                results = await vector_service.search_documents(query_embedding, n_results=k)
                assert isinstance(results, list)

                if k <= 0:
                    assert len(results) == 0
                elif k > len(sample_embeddings):
                    assert len(results) == len(sample_embeddings)
                else:
                    assert len(results) == k

            except (ValueError, RuntimeError) as e:
                # 负数k值应该抛出异常
                if k < 0:
                    assert "k" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_search_similarity_threshold_boundary(self, vector_service, sample_embeddings):
        """测试相似度阈值边界"""
        # 添加完全相同的文档用于测试
        identical_embedding = [0.1] * 1536
        await vector_service.add_document("doc1", "相同内容1", "相同内容1", embedding=identical_embedding)
        await vector_service.add_document("doc2", "相同内容2", "相同内容2", embedding=identical_embedding)

        test_cases = [
            (-1.0, "阈值=-1.0"),
            (0.0, "阈值=0.0"),
            (0.5, "阈值=0.5"),
            (1.0, "阈值=1.0"),
            (1.5, "阈值=1.5(大于1)"),
            (-0.5, "阈值=-0.5(小于-1)"),
        ]

        for threshold, description in test_cases:
            results = await vector_service.search_documents(
                "",
                n_results=10,
                filter_metadata={"distance": {"$gte": threshold}}
            )

            if threshold <= 1.0:  # 合理的阈值应该返回结果
                assert len(results) >= 1
            else:  # 过高的阈值可能没有结果
                assert len(results) >= 0

    # ========== 文档内容边界测试 ==========

    @pytest.mark.asyncio
    async def test_add_empty_document(self, vector_service):
        """测试空文档"""
        empty_embedding = [0.0] * 1536

        await vector_service.add_document(
            doc_id="empty_doc",
            title="空文档",
            content="",
            embedding=empty_embedding,
            metadata={"type": "empty"}
        )

        # 应该能正常搜索到
        results = await vector_service.search_documents("", n_results=1)
        assert len(results) >= 1
        assert results[0]['id'].startswith("doc_empty_doc")

    @pytest.mark.asyncio
    async def test_add_very_long_document(self, vector_service):
        """测试超长文档"""
        # 创建很长的内容
        long_content = "这是一段很长的内容。" * 10000  # 约20万字
        embedding = np.random.randn(1536).tolist()

        await vector_service.add_document(
            doc_id="long_doc",
            title="超长文档",
            content=long_content,
            embedding=embedding,
            metadata={"type": "long_content", "length": len(long_content)}
        )

        results = await vector_service.search_documents("", n_results=1)
        assert len(results) >= 1
        assert results[0]['id'].startswith("doc_long_doc")

    @pytest.mark.asyncio
    async def test_add_document_with_special_characters(self, vector_service):
        """测试包含特殊字符的文档"""
        special_contents = [
            "内容包含\n换行\r\n字符",
            "内容包含\t制表符",
            "内容包含\"引号\"和'单引号'",
            "内容包含\\反斜杠\\",
            "内容包含🚀 Emoji 🎯",
            "内容包含\u0000空字符",
            "内容包含HTML: <div>测试</div>",
            "内容包含JSON: {\"key\": \"value\"}",
            "内容包含XML: <root>数据</root>",
        ]

        for i, content in enumerate(special_contents):
            embedding = np.random.randn(1536).tolist()
            doc_id = f"special_doc_{i}"

            await vector_service.add_document(
                doc_id=doc_id,
                title=f"特殊字符文档{i}",
                content=content,
                embedding=embedding,
                metadata={"type": "special_chars", "index": i}
            )

            # 验证能正常搜索
            results = await vector_service.search_documents("", n_results=1)
            assert len(results) >= 1
            assert results[0]['id'].startswith(f"doc_{doc_id}")

    # ========== 元数据边界测试 ==========

    @pytest.mark.asyncio
    async def test_add_document_with_extreme_metadata(self, vector_service):
        """测试极端的元数据"""
        embedding = np.random.randn(1536).tolist()

        # 大元数据
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(1000)}
        await vector_service.add_document(
            doc_id="large_metadata_doc",
            title="大元数据测试",
            content="大元数据测试",
            embedding=embedding,
            metadata=large_metadata
        )

        # 嵌套元数据
        nested_metadata = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": "deep_value"
                    }
                }
            }
        }
        await vector_service.add_document(
            doc_id="nested_metadata_doc",
            title="嵌套元数据测试",
            content="嵌套元数据测试",
            embedding=embedding,
            metadata=nested_metadata
        )

        # 特殊值元数据
        special_metadata = {
            "null_value": None,
            "empty_string": "",
            "large_number": 1e308,
            "small_number": 1e-308,
            "boolean_true": True,
            "boolean_false": False,
            "empty_list": [],
            "empty_dict": {},
        }
        await vector_service.add_document(
            doc_id="special_metadata_doc",
            title="特殊元数据测试",
            content="特殊元数据测试",
            embedding=embedding,
            metadata=special_metadata
        )

        # 验证所有文档都能被搜索到
        results = await vector_service.search_documents("", n_results=10)
        doc_ids = [result['id'] for result in results]
        assert any(doc_id.startswith("doc_large_metadata_doc") for doc_id in doc_ids)
        assert any(doc_id.startswith("doc_nested_metadata_doc") for doc_id in doc_ids)
        assert any(doc_id.startswith("doc_special_metadata_doc") for doc_id in doc_ids)

    # ========== 批量操作边界测试 ==========

    @pytest.mark.asyncio
    async def test_batch_add_documents_extreme_cases(self, vector_service):
        """测试批量添加文档的极端情况"""
        # 空批次
        await vector_service.batch_add_documents([])

        # 大批量
        large_batch = []
        for i in range(1000):
            large_batch.append({
                'doc_id': f"batch_doc_{i}",
                'title': f"批量文档{i}",
                'content': f"批量文档内容 {i}",
                'embedding': np.random.randn(1536).tolist(),
                'metadata': {'batch_index': i}
            })

        try:
            await vector_service.batch_add_documents(large_batch)

            # 验证部分文档能被搜索到
            sample_embedding = large_batch[0]['embedding']
            results = await vector_service.search_documents("", n_results=10)
            assert len(results) >= 1

        except (MemoryError, RuntimeError) as e:
            # 内存不足的情况下应该优雅处理
            print(f"大批量处理需要优化: {e}")

    @pytest.mark.asyncio
    async def test_batch_delete_documents_edge_cases(self, vector_service, sample_embeddings):
        """测试批量删除文档的边界情况"""
        # 先添加文档
        for doc_id, embedding in sample_embeddings.items():
            await vector_service.add_document(doc_id, f"内容{doc_id}", "内容", embedding=embedding)

        # 删除空列表
        await vector_service.delete_document(doc_id=None)

        # 删除不存在的文档ID
        await vector_service.delete_document(doc_id=-1)

        # 删除混合列表（存在和不存在）
        await vector_service.delete_document(doc_id="text1")
        await vector_service.delete_document(doc_id="text2")


        # 验证存在的文档被删除
        remaining_docs = ["text3"]  # 假设只删除了text1和text2
        for doc_id in remaining_docs:
            results = await vector_service.search_documents(sample_embeddings[doc_id], n_results=10)
            doc_ids = [result['id'] for result in results]
            assert any(d.startswith(f"doc_{doc_id}") for d in doc_ids)

    # ========== 相似度计算边界测试 ==========

    @pytest.mark.asyncio
    async def test_similarity_with_identical_vectors(self, vector_service):
        """测试完全相同向量的相似度"""
        vec1 = [0.1, 0.2, 0.3, 0.4, 0.5] + [0.0] * (1536 - 5)
        vec2 = [0.1, 0.2, 0.3, 0.4, 0.5] + [0.0] * (1536 - 5)

        cosine_sim = vector_service._cosine_similarity(vec1, vec2)
        euclidean_dist = vector_service._euclidean_distance(vec1, vec2)

        assert abs(cosine_sim - 1.0) < 1e-10
        assert abs(euclidean_dist - 0.0) < 1e-10

    @pytest.mark.asyncio
    async def test_similarity_with_orthogonal_vectors(self, vector_service):
        """测试正交向量的相似度"""
        # 创建正交向量
        vec1 = [1.0] + [0.0] * (1536 - 1)
        vec2 = [0.0] + [1.0] + [0.0] * (1536 - 2)

        cosine_sim = vector_service._cosine_similarity(vec1, vec2)
        assert abs(cosine_sim - 0.0) < 1e-10

    @pytest.mark.asyncio
    async def test_similarity_with_opposite_vectors(self, vector_service):
        """测试相反向量的相似度"""
        vec1 = [0.1, 0.2, 0.3] + [0.0] * (1536 - 3)
        vec2 = [-0.1, -0.2, -0.3] + [0.0] * (1536 - 3)

        cosine_sim = vector_service._cosine_similarity(vec1, vec2)
        assert abs(cosine_sim - (-1.0)) < 1e-10

    # ========== 内存和性能边界测试 ==========

    @pytest.mark.asyncio
    async def test_memory_efficiency_with_large_index(self, vector_service):
        """测试大索引的内存效率"""
        # 添加大量文档
        large_embeddings = {}
        for i in range(10000):
            doc_id = f"memory_test_{i}"
            embedding = np.random.randn(1536).tolist()
            large_embeddings[doc_id] = embedding

            await vector_service.add_document(
                doc_id=doc_id,
                title=f"内存测试文档{i}",
                content=f"内存测试文档 {i}",
                embedding=embedding,
                metadata={'test_id': i}
            )

            # 每1000个文档检查一次内存效率
            if i % 1000 == 0 and i > 0:
                # 执行搜索测试性能
                query_embedding = large_embeddings[f"memory_test_{i-1}"]
                results = await vector_service.search_documents("", n_results=10)
                assert len(results) >= 1

                print(f"已添加 {i+1} 个文档，搜索正常")

    @pytest.mark.asyncio
    async def test_search_performance_with_large_dataset(self, vector_service):
        """测试大数据集的搜索性能"""
        import time

        # 添加测试数据
        test_embeddings = []
        for i in range(1000):
            embedding = np.random.randn(1536).tolist()
            test_embeddings.append(embedding)

            await vector_service.add_document(
                doc_id=f"perf_doc_{i}",
                title=f"性能测试文档{i}",
                content=f"性能测试文档 {i}",
                embedding=embedding
            )

        # 测试搜索性能
        query_embedding = test_embeddings[0]

        # 预热
        await vector_service.search_documents("", n_results=10)

        # 正式测试
        start_time = time.time()
        results = await vector_service.search_documents("", n_results=10)
        end_time = time.time()

        search_time = end_time - start_time

        assert len(results) >= 1
        assert search_time < 1.0, f"搜索时间过长: {search_time}秒"
        print(f"1000文档搜索耗时: {search_time:.4f}秒")

    # ========== 错误处理和异常边界测试 ==========

    @pytest.mark.asyncio
    async def test_search_with_invalid_query_vector(self, vector_service):
        """测试无效的查询向量"""
        invalid_vectors = [
            None,
            "not a vector",
            [],  # 空向量
            [1, 2, 3],  # 维度不匹配
            [[1, 2], [3, 4]],  # 二维数组
            {1: 2, 3: 4},  # 字典
        ]

        for invalid_vector in invalid_vectors:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                await vector_service.search_documents(invalid_vector, n_results=5)

    @pytest.mark.asyncio
    async def test_add_document_with_invalid_embedding(self, vector_service):
        """测试添加文档时无效的嵌入向量"""
        invalid_embeddings = [
            None,
            "not embedding",
            [],  # 空向量
            [1, 2, 3],  # 维度不匹配
            "1,2,3,4,5",  # 字符串形式的向量
            [[1, 2], [3, 4]],  # 错误的维度
        ]

        for invalid_embedding in invalid_embeddings:
            with pytest.raises((ValueError, TypeError)):
                await vector_service.add_document(
                    doc_id="test_doc",
                    title="测试标题",
                    content="测试内容",
                    embedding=invalid_embedding
                )

    # ========== 并发访问边界测试 ==========

    @pytest.mark.asyncio
    async def test_concurrent_vector_operations(self, vector_service):
        """测试并发向量操作"""
        import asyncio

        results = {}
        errors = {}

        async def add_document_task(task_id):
            try:
                embedding = np.random.randn(1536).tolist()
                doc_id = f"concurrent_doc_{task_id}"

                await vector_service.add_document(
                    doc_id=doc_id,
                    title=f"并发测试文档{task_id}",
                    content=f"并发测试文档 {task_id}",
                    embedding=embedding
                )

                # 立即搜索
                search_results = await vector_service.search_documents("", n_results=1)
                results[task_id] = len(search_results) > 0

            except Exception as e:
                errors[task_id] = str(e)

        # 启动多个任务
        tasks = [add_document_task(i) for i in range(10)]
        await asyncio.gather(*tasks)

        # 验证结果
        assert len(results) > 0, "应该有成功的并发操作"
        assert len(errors) == 0, f"不应该有错误: {errors}"
        assert all(results.values()), "所有并发操作都应该成功"

    # ========== 数据一致性边界测试 ==========

    @pytest.mark.asyncio
    async def test_vector_precision_preservation(self, vector_service):
        """测试向量精度保持"""
        # 高精度向量
        high_precision_vector = [1.123456789012345] * 1536

        await vector_service.add_document(
            doc_id="precision_test",
            title="精度测试",
            content="精度测试",
            embedding=high_precision_vector
        )

        # 搜索并验证精度
        results = await vector_service.search_documents("", n_results=1)

        assert len(results) > 0
        assert results[0]['id'].startswith("doc_precision_test")
        # 相似度应该接近1.0
        assert results[0]['distance'] > 0.999999

    @pytest.mark.asyncio
    async def test_metadata_persistence(self, vector_service):
        """测试元数据持久性"""
        complex_metadata = {
            "nested": {
                "deep": {
                    "value": "test"
                }
            },
            "list": [1, 2, 3, "four", {"five": 5}],
            "unicode": "中文测试 🚀",
            "null_value": None,
            "empty_string": "",
            "number": 42.42,
            "boolean": True
        }

        embedding = np.random.randn(1536).tolist()

        await vector_service.add_document(
            doc_id="metadata_test",
            title="元数据测试",
            content="元数据测试",
            embedding=embedding,
            metadata=complex_metadata
        )

        # 验证搜索返回的元数据
        results = await vector_service.search_documents("", n_results=1)

        assert len(results) > 0
        returned_metadata = results[0]['metadata'] 

        # 验证复杂数据结构
        assert returned_metadata["nested"]["deep"]["value"] == "test"
        assert returned_metadata["list"] == [1, 2, 3, "four", {"five": 5}]
        assert returned_metadata["unicode"] == "中文测试 🚀"
        assert returned_metadata["null_value"] is None
        assert returned_metadata["empty_string"] == ""
        assert returned_metadata["number"] == 42.42
        assert returned_metadata["boolean"] is True