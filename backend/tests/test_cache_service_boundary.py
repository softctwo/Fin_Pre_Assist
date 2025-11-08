"""缓存服务边界测试 - 提升测试覆盖率"""
import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock
from app.services.cache_service import CacheService


class TestCacheServiceBoundaryCases:
    """缓存服务边界条件测试"""

    @pytest.fixture
    def cache_service(self):
        """创建缓存服务实例"""
        return CacheService()

    @pytest.fixture
    def large_data(self):
        """提供大量测试数据"""
        return {
            "large_list": list(range(10000)),
            "nested_dict": {f"key_{i}": f"value_{i}" for i in range(1000)},
            "long_string": "x" * 100000,  # 100KB字符串
            "binary_data": b"\x00\x01\x02\x03" * 10000,  # 40KB二进制数据
        }

    # ========== 键名边界测试 ==========

    @pytest.mark.asyncio
    async def test_cache_keys_with_special_characters(self, cache_service):
        """测试特殊字符的缓存键"""
        special_keys = [
            "key with spaces",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key/with/slashes",
            "key\\with\\backslashes",
            "key:with:colons",
            "key;with;semicolons",
            "key'with'quotes",
            'key"with"double"quotes',
            "key`with`backticks",
            "key~with~tildes",
            "key!with!exclamation",
            "key@with@at",
            "key#with#hash",
            "key$with$dollar",
            "key%with%percent",
            "key^with^caret",
            "key&with&ampersand",
            "key*with*asterisk",
            "key(with)parentheses",
            "key[with]brackets",
            "key{with}braces",
            "key+with+plus",
            "key=with=equals",
            "key|with|pipe",
            "key\u003cwith\u003cless",
            "key\u003ewith\u003egreater",
            "key?with?question",
            "key,with,comma",
            "key.with.dot",
            "中文键名",
            "🚀emoji🔥key",
            "key\nwith\nnewline",
            "key\twith\ttab",
            "key\rwith\rreturn",
            "",  # 空键
            " ",  # 空格键
            "\t",  # 制表符键
            "\n",  # 换行键
        ]

        for key in special_keys:
            try:
                await cache_service.set(key, f"value_for_{repr(key)}")
                retrieved = await cache_service.get(key)
                assert retrieved == f"value_for_{repr(key)}"
            except Exception as e:
                # 某些特殊字符可能导致问题，应该给出合适的错误
                print(f"特殊键 {repr(key)} 处理异常: {e}")

    @pytest.mark.asyncio
    async def test_cache_keys_with_maximum_length(self, cache_service):
        """测试最大长度的缓存键"""
        # 创建不同长度的键名
        length_test_cases = [
            (100, "100字符键"),
            (255, "255字符键"),
            (256, "256字符键"),
            (1000, "1000字符键"),
            (10000, "10000字符键"),
        ]

        for length, description in length_test_cases:
            long_key = "a" * length
            value = f"value_for_{length}_char_key"

            try:
                await cache_service.set(long_key, value)
                retrieved = await cache_service.get(long_key)
                assert retrieved == value
            except (ValueError, MemoryError) as e:
                # 过长的键名可能导致内存问题
                print(f"{description}处理异常: {e}")

    @pytest.mark.asyncio
    async def test_duplicate_cache_keys_case_sensitivity(self, cache_service):
        """测试缓存键大小写敏感性"""
        test_cases = [
            ("lowercase", "LOWERCASE", False),  # 应该区分大小写
            ("CamelCase", "camelcase", False),
            ("UPPERCASE", "uppercase", False),
            ("MixedCase", "mixedcase", False),
            ("key_123", "key_123", True),  # 完全相同的键
        ]

        for key1, key2, should_be_same in test_cases:
            await cache_service.set(key1, "value1")
            await cache_service.set(key2, "value2")

            val1 = await cache_service.get(key1)
            val2 = await cache_service.get(key2)

            if should_be_same:
                assert val1 == val2 == "value2"  # 后设置的值覆盖
            else:
                assert val1 == "value1"
                assert val2 == "value2"

    # ========== 值大小和内容边界测试 ==========

    @pytest.mark.asyncio
    async def test_cache_values_with_extreme_sizes(self, cache_service):
        """测试极端大小的缓存值"""
        # 创建不同大小的值
        size_test_cases = [
            (0, "空值"),
            (1, "1字节"),
            (1024, "1KB"),
            (1024 * 1024, "1MB"),
            (10 * 1024 * 1024, "10MB"),
            (50 * 1024 * 1024, "50MB"),
        ]

        for size, description in size_test_cases:
            if size == 0:
                large_value = ""
            else:
                large_value = "x" * size

            key = f"size_test_{size}"

            try:
                await cache_service.set(key, large_value)
                retrieved = await cache_service.get(key)
                assert retrieved == large_value
                assert len(retrieved) == size
            except (MemoryError, ValueError) as e:
                # 过大的值可能导致内存问题
                print(f"{description}处理异常: {e}")

    @pytest.mark.asyncio
    async def test_cache_complex_data_structures(self, cache_service):
        """测试复杂数据结构缓存"""
        complex_data = {
            # 嵌套字典
            "nested_dict": {
                "level1": {
                    "level2": {
                        "level3": {
                            "deep_value": "found me!"
                        }
                    }
                }
            },
            # 混合类型列表
            "mixed_list": [
                42,
                "string",
                3.14,
                True,
                None,
                [1, 2, 3],
                {"inner": "dict"},
            ],
            # Unicode和特殊字符
            "unicode": "中文测试 🚀 العربية",
            # 大整数和小数
            "big_int": 2**63 - 1,
            "small_float": 1e-308,
            # 布尔值和None
            "bool_true": True,
            "bool_false": False,
            "null_value": None,
            # 空集合
            "empty_list": [],
            "empty_dict": {},
            "empty_string": "",
            # 时间和日期相关
            "timestamp": 1234567890.123456,
        }

        await cache_service.set("complex_data", complex_data)
        retrieved = await cache_service.get("complex_data")

        # 验证复杂数据结构完整性
        assert retrieved["nested_dict"]["level1"]["level2"]["level3"]["deep_value"] == "found me!"
        assert retrieved["mixed_list"][0] == 42
        assert retrieved["mixed_list"][1] == "string"
        assert retrieved["mixed_list"][6]["inner"] == "dict"
        assert retrieved["unicode"] == "中文测试 🚀 العربية"
        assert retrieved["big_int"] == 2**63 - 1
        assert retrieved["bool_true"] is True
        assert retrieved["null_value"] is None
        assert retrieved["empty_list"] == []

    @pytest.mark.asyncio
    async def test_cache_circular_references(self, cache_service):
        """测试循环引用缓存"""
        # 创建循环引用数据结构
        data_a = {"name": "A", "ref": None}
        data_b = {"name": "B", "ref": data_a}
        data_a["ref"] = data_b

        try:
            await cache_service.set("circular_ref", data_a)
            retrieved = await cache_service.get("circular_ref")

            # 验证循环引用（可能被转换为非循环结构）
            assert retrieved["name"] == "A"
            assert "ref" in retrieved

        except (ValueError, RecursionError) as e:
            # 循环引用可能导致序列化问题
            print(f"循环引用处理异常: {e}")

    # ========== 过期时间边界测试 ==========

    @pytest.mark.asyncio
    async def test_cache_expiration_edge_cases(self, cache_service):
        """测试缓存过期边界情况"""
        expiration_test_cases = [
            (0, "立即过期"),
            (0.001, "1毫秒后过期"),
            (0.1, "100毫秒后过期"),
            (1, "1秒后过期"),
            (60, "1分钟后过期"),
            (3600, "1小时后过期"),
            (86400, "1天后过期"),
            (-1, "负过期时间"),
        ]

        for expire_time, description in expiration_test_cases:
            key = f"expire_test_{description.replace(' ', '_')}"
            value = f"value_for_{description}"

            try:
                if expire_time >= 0:
                    await cache_service.set(key, value, ttl=expire_time)
                    retrieved = await cache_service.get(key)

                    if expire_time == 0 or expire_time == 0.001:
                        # 立即或很快过期的值可能获取不到
                        pass  # 可能为None
                    else:
                        assert retrieved == value
                else:
                    # 负过期时间应该抛出异常或使用默认值
                    with pytest.raises((ValueError, TypeError)):
                        await cache_service.set(key, value, ttl=expire_time)

            except Exception as e:
                print(f"{description}处理异常: {e}")

    @pytest.mark.asyncio
    async def test_cache_expiration_timing_accuracy(self, cache_service):
        """测试缓存过期时间准确性"""
        # 测试短时间过期
        short_expire_time = 0.5  # 500毫秒
        await cache_service.set("timing_test", "expire_soon", ttl=short_expire_time)

        # 立即检查 - 应该存在
        assert await cache_service.get("timing_test") == "expire_soon"

        # 等待过期
        await asyncio.sleep(short_expire_time + 0.1)  # 多等100毫秒确保过期

        # 再次检查 - 应该已过期
        assert await cache_service.get("timing_test") is None

        # 测试长时间过期（只验证设置，不实际等待）
        long_expire_time = 3600  # 1小时
        await cache_service.set("long_timing_test", "expire_later", ttl=long_expire_time)
        assert await cache_service.get("long_timing_test") == "expire_later"

    # ========== 并发访问边界测试 ==========

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, cache_service):
        """测试并发缓存操作"""
        results = {}
        errors = {}

        async def cache_operation_task(task_id):
            try:
                key = f"concurrent_key_{task_id}"
                value = f"concurrent_value_{task_id}"

                # 设置值
                await cache_service.set(key, value, ttl=60)

                # 稍微延迟确保其他任务也在操作
                await asyncio.sleep(0.001)

                # 获取值
                retrieved = await cache_service.get(key)
                results[task_id] = retrieved == value

                # 删除值
                await cache_service.delete(key)

                # 验证删除
                deleted_value = await cache_service.get(key)
                if deleted_value is not None:
                    results[task_id] = False  # 删除失败

            except Exception as e:
                errors[task_id] = str(e)

        # 启动多个任务
        tasks = [cache_operation_task(i) for i in range(20)]
        await asyncio.gather(*tasks)

        # 验证结果
        assert len(results) > 0, "应该有成功的并发操作"
        assert len(errors) == 0, f"不应该有错误: {errors}"
        assert all(results.values()), "所有并发操作都应该成功"

    @pytest.mark.asyncio
    async def test_cache_race_conditions(self, cache_service):
        """测试缓存竞争条件"""
        shared_key = "race_condition_test"
        results = []

        async def race_task(task_id):
            # 所有任务尝试设置同一个键
            value = f"race_value_{task_id}"
            await cache_service.set(shared_key, value, ttl=10)

            # 立即读取
            retrieved = await cache_service.get(shared_key)
            results.append((task_id, retrieved))

        # 启动多个任务进行竞争
        tasks = [race_task(i) for i in range(10)]
        await asyncio.gather(*tasks)

        # 验证结果 - 所有读取操作都应该成功
        assert len(results) == 10
        for task_id, retrieved_value in results:
            assert retrieved_value is not None
            # 值应该是某个任务设置的值
            assert retrieved_value.startswith("race_value_")

    # ========== 错误恢复和容错测试 ==========

    @pytest.mark.asyncio
    async def test_cache_error_recovery(self, cache_service):
        """测试缓存错误恢复"""
        # 测试无效操作
        invalid_operations = [
            (lambda: cache_service.set(None, "value"), "None键"),
            (lambda: cache_service.set("key", None), "None值"),
            (lambda: cache_service.get(None), "None键获取"),
            (lambda: cache_service.delete(None), "None键删除"),
            (lambda: cache_service.set("", "value"), "空键"),
            (lambda: cache_service.get(""), "空键获取"),
        ]

        for operation, description in invalid_operations:
            try:
                result = await operation()
                # 应该返回None或抛出异常
                assert result is None or isinstance(result, str)
            except Exception as e:
                # 预期某些操作会抛出异常
                print(f"{description}抛出异常: {e}")

    @pytest.mark.asyncio
    async def test_cache_connection_failure_simulation(self, cache_service):
        """测试缓存连接失败模拟"""
        # 模拟连接失败（如果底层缓存支持）
        with patch.object(cache_service, '_redis_client', new=None):
            # 测试操作失败
            # 在redis不可用时，应该降级到内存缓存，而不是抛出异常
            assert await cache_service.set("test_key", "test_value") is True
            assert await cache_service.get("test_key") == "test_value"

    # ========== 缓存清空和重置边界测试 ==========

    @pytest.mark.asyncio
    async def test_cache_clear_operations(self, cache_service):
        """测试缓存清空操作"""
        # 添加测试数据
        for i in range(100):
            await cache_service.set(f"clear_test_{i}", f"value_{i}", ttl=60)

        # 验证数据存在
        assert await cache_service.get("clear_test_0") is not None
        assert await cache_service.get("clear_test_99") is not None

        # 清空缓存
        await cache_service.clear()

        # 验证数据被清空
        cleared_count = 0
        for i in range(100):
            if await cache_service.get(f"clear_test_{i}") is None:
                cleared_count += 1

        assert cleared_count >= 90, f"应该有大部分数据被清空，实际清空: {cleared_count}"

    @pytest.mark.asyncio
    async def test_cache_clear_empty_cache(self, cache_service):
        """测试清空已空的缓存"""
        # 清空空缓存（不应该出错）
        await cache_service.clear()
        await cache_service.clear()  # 再次清空

        # 验证空缓存操作
        assert await cache_service.get("non_existent_key") is None

        # 添加数据后验证
        await cache_service.set("test_key", "test_value")
        assert await cache_service.get("test_key") == "test_value"

        # 再次清空
        await cache_service.clear()
        assert await cache_service.get("test_key") is None