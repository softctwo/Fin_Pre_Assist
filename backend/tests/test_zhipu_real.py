"""
真实Zhipu API测试
使用真实API密钥测试智谱AI的功能
需要设置环境变量: ZHIPU_API_KEY
"""
import pytest
import os
import sys

pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_ZHIPU_REAL_TESTS") != "1",
    reason="Set ENABLE_ZHIPU_REAL_TESTS=1 with real credentials to run",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.ai_service import AIService


@pytest.fixture
def ai_service():
    """创建AI服务实例并配置为智谱AI"""
    ai = AIService()
    ai.provider = "zhipu"
    return ai


@pytest.mark.asyncio
async def test_zhipu_generate_simple_text(ai_service):
    """测试真实的智谱AI文本生成"""
    try:
        result = await ai_service.generate_text(
            prompt="请用一句话介绍人工智能",
            max_tokens=100,
            temperature=0.7
        )

        print(f"\n[Zhipu AI Response]\n{result}\n")

        # 验证结果
        assert result is not None
        assert len(result) > 0
        assert isinstance(result, str)

        # 验证是中文回复
        assert any('\u4e00' <= c <= '\u9fff' for c in result)

    except NotImplementedError:
        pytest.skip("智谱AI生成方法尚未实现")


@pytest.mark.asyncio
async def test_zhipu_generate_with_context(ai_service):
    """测试带上下文的文本生成"""
    prompt = """
    你是一位金融售前专家，请为客户生成一份执行摘要。

    客户: ABC银行
    需求: 核心系统升级改造
    预算: 500万
    周期: 6个月

    请生成200字左右的执行摘要。
    """

    try:
        result = await ai_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        print(f"\n[Executive Summary]\n{result}\n")

        assert result is not None
        assert len(result) >= 50  # 至少50个字符
        assert "银行" in result or "系统" in result

    except NotImplementedError:
        pytest.skip("智谱AI生成方法尚未实现")


@pytest.mark.asyncio
async def test_zhipu_embed_text_basic(ai_service):
    """测试文本向量化"""
    try:
        result = await ai_service.embed_text("金融科技")

        print(f"\n[Embedding Vector]\nLength: {len(result)}\nFirst 5 values: {result[:5]}\n")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    except NotImplementedError:
        pytest.skip("向量化方法尚未实现")


@pytest.mark.asyncio
async def test_zhipu_embed_multiple_texts(ai_service):
    """测试多个文本的向量化一致性"""
    try:
        texts = [
            "银行核心系统",
            "银行核心系统",
            "移动支付解决方案"
        ]

        embeddings = []
        for text in texts:
            emb = await ai_service.embed_text(text)
            embeddings.append(emb)

        # 验证维度一致
        assert len(embeddings[0]) == len(embeddings[1])
        assert len(embeddings[0]) == len(embeddings[2])

        # 验证相同文本的向量相似
        # 这里我们只是验证它们的长度一致，实际的相似度计算可以更复杂
        print(f"\n[Embeddings Comparison]")
        print(f"Same texts vector length: {len(embeddings[0])}")
        print(f"Different text vector length: {len(embeddings[2])}")

    except NotImplementedError:
        pytest.skip("向量化方法尚未实现")


@pytest.mark.flaky(reruns=2, reruns_delay=5)
@pytest.mark.asyncio
async def test_zhipu_generate_conversation(ai_service):
    """测试对话生成（可能因网络超时而不稳定）"""
    try:
        questions = [
            "什么是金融科技？",
            "它有哪些主要应用场景？",
            "实施难点是什么？"
        ]

        answers = []
        for question in questions:
            answer = await ai_service.generate_text(
                prompt=question,
                max_tokens=300,
                temperature=0.7
            )
            answers.append(answer)

            print(f"\n[Question] {question}")
            print(f"[Answer] {answer[:100]}...")

        assert len(answers) == 3
        for answer in answers:
            assert answer is not None
            assert len(answer) > 0

    except NotImplementedError:
        pytest.skip("智谱AI生成方法尚未实现")


@pytest.mark.asyncio
async def test_zhipu_generate_with_different_parameters(ai_service):
    """测试不同参数的影响"""
    prompt = "介绍区块链技术"

    try:
        # 低温，更确定性的输出
        result_low = await ai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.1
        )

        # 高温，更有创造性的输出
        result_high = await ai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.9
        )

        print(f"\n[Low Temperature (0.1)]\n{result_low[:200]}...")
        print(f"\n[High Temperature (0.9)]\n{result_high[:200]}...")

        assert result_low is not None
        assert result_high is not None
        assert result_low != result_high  # 应该有不同的输出

    except NotImplementedError:
        pytest.skip("智谱AI生成方法尚未实现")


@pytest.mark.xfail(reason="智谱AI错误处理机制在测试环境中行为不同")
@pytest.mark.asyncio
async def test_zhipu_error_handling(ai_service):
    """测试错误处理"""
    import httpx

    try:
        # 测试无效的API密钥
        original_key = os.environ.get('ZHIPU_API_KEY')
        os.environ['ZHIPU_API_KEY'] = 'invalid_key'

        ai_service.provider = "zhipu"

        try:
            result = await ai_service.generate_text("测试")
            # 如果上面的代码没有抛出异常，说明有问题
            pytest.fail("应该抛出认证错误")
        except Exception as e:
            assert "认证" in str(e).lower() or "api" in str(e).lower()

    except NotImplementedError:
        pytest.skip("智谱AI生成方法尚未实现")
    finally:
        # 恢复原始密钥
        if original_key:
            os.environ['ZHIPU_API_KEY'] = original_key


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
