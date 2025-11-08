"""性能基准测试 - 建立系统性能基准"""
import pytest
import time
import asyncio
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models import User, UserRole, Template, TemplateType, KnowledgeBase, Proposal, ProposalStatus
from app.api.auth import get_password_hash


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_performance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.results: List[Dict[str, Any]] = []
        
    def setup_test_data(self):
        """设置测试数据"""
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        
        # 创建测试用户
        user = User(
            username="perfuser",
            email="perf@example.com",
            password_hash=get_password_hash("testpass123"),
            role=UserRole.USER,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建测试模板
        for i in range(10):
            template = Template(
                name=f"性能测试模板{i}",
                type=TemplateType.PROPOSAL,
                description=f"性能测试用模板{i}",
                content="客户: {{ customer_name }}\n需求: {{ requirements }}",
                variables={"customer_name": "string", "requirements": "string"}
            )
            db.add(template)
        
        # 创建测试知识
        for i in range(20):
            knowledge = KnowledgeBase(
                category="性能测试",
                title=f"性能测试知识{i}",
                content=f"这是性能测试知识{i}的详细内容",
                tags=["性能", "测试", f"标签{i}"]
            )
            db.add(knowledge)
        
        # 创建测试方案
        for i in range(15):
            proposal = Proposal(
                title=f"性能测试方案{i}",
                customer_name=f"测试客户{i}",
                customer_industry="科技",
                requirements=f"性能测试需求{i}",
                status=ProposalStatus.DRAFT
            )
            db.add(proposal)
        
        db.commit()
        db.close()
        
        # 获取认证token
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": "perfuser", "password": "testpass123"}
        )
        self.auth_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def cleanup_test_data(self):
        """清理测试数据"""
        Base.metadata.drop_all(bind=engine)
    
    def measure_response_time(self, func, *args, **kwargs) -> Dict[str, Any]:
        """测量响应时间"""
        start_time = time.time()
        try:
            response = func(*args, **kwargs)
            end_time = time.time()
            return {
                "response": response,  # 保存原始响应对象
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "response_size": len(response.content) if hasattr(response, 'content') else 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "response": None,
                "response_time": end_time - start_time,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "response_size": 0
            }
    
    def run_concurrent_test(self, func, num_threads: int = 10, requests_per_thread: int = 5) -> Dict[str, Any]:
        """运行并发测试"""
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for _ in range(num_threads * requests_per_thread):
                future = executor.submit(self.measure_response_time, func)
                futures.append(future)
            
            results = []
            for future in futures:
                result = future.result()
                results.append(result)
        
        response_times = [r["response_time"] for r in results if r["success"]]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        return {
            "total_requests": len(results),
            "successful_requests": sum(1 for r in results if r["success"]),
            "success_rate": success_rate,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            "requests_per_second": len(results) / (max(response_times) - min(response_times)) if response_times else 0
        }


@pytest.fixture
def perf_benchmark():
    """性能基准测试fixture"""
    benchmark = PerformanceBenchmark()
    benchmark.setup_test_data()
    yield benchmark
    benchmark.cleanup_test_data()


class TestAPIPerformance:
    """API性能测试"""
    
    def test_auth_login_performance(self, perf_benchmark):
        """测试登录接口性能"""
        def login_request():
            return perf_benchmark.client.post(
                "/api/v1/auth/login",
                data={"username": "perfuser", "password": "testpass123"}
            )
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(login_request)
        assert single_result["success"]
        assert single_result["response_time"] < 1.0  # 1秒内响应
        
        # 并发性能测试
        concurrent_results = perf_benchmark.run_concurrent_test(login_request, num_threads=20, requests_per_thread=3)
        
        perf_benchmark.results.append({
            "test_name": "auth_login",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言
        assert concurrent_results["success_rate"] > 0.95  # 95%成功率
        assert concurrent_results["avg_response_time"] < 2.0  # 平均响应时间小于2秒
        assert concurrent_results["p95_response_time"] < 5.0  # 95%请求在5秒内完成
    
    def test_templates_list_performance(self, perf_benchmark):
        """测试模板列表接口性能"""
        def list_templates():
            return perf_benchmark.client.get("/api/v1/templates/", headers=perf_benchmark.auth_headers)
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(list_templates)
        assert single_result["success"]
        assert single_result["response_time"] < 0.5  # 500ms内响应
        
        # 并发性能测试
        concurrent_results = perf_benchmark.run_concurrent_test(list_templates, num_threads=15, requests_per_thread=5)
        
        perf_benchmark.results.append({
            "test_name": "templates_list",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言
        assert concurrent_results["success_rate"] > 0.95
        assert concurrent_results["avg_response_time"] < 1.0
        assert concurrent_results["p95_response_time"] < 2.0
    
    def test_knowledge_list_performance(self, perf_benchmark):
        """测试知识库列表接口性能"""
        def list_knowledge():
            return perf_benchmark.client.get("/api/v1/knowledge/", headers=perf_benchmark.auth_headers)
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(list_knowledge)
        assert single_result["success"]
        assert single_result["response_time"] < 0.5
        
        # 并发性能测试
        concurrent_results = perf_benchmark.run_concurrent_test(list_knowledge, num_threads=15, requests_per_thread=5)
        
        perf_benchmark.results.append({
            "test_name": "knowledge_list",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言
        assert concurrent_results["success_rate"] > 0.95
        assert concurrent_results["avg_response_time"] < 1.0
        assert concurrent_results["p95_response_time"] < 2.0
    
    def test_proposals_list_performance(self, perf_benchmark):
        """测试方案列表接口性能"""
        def list_proposals():
            return perf_benchmark.client.get("/api/v1/proposals/", headers=perf_benchmark.auth_headers)
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(list_proposals)
        assert single_result["success"]
        assert single_result["response_time"] < 0.5
        
        # 并发性能测试
        concurrent_results = perf_benchmark.run_concurrent_test(list_proposals, num_threads=15, requests_per_thread=5)
        
        perf_benchmark.results.append({
            "test_name": "proposals_list",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言
        assert concurrent_results["success_rate"] > 0.95
        assert concurrent_results["avg_response_time"] < 1.0
        assert concurrent_results["p95_response_time"] < 2.0
    
    def test_template_creation_performance(self, perf_benchmark):
        """测试模板创建性能"""
        def create_template():
            return perf_benchmark.client.post(
                "/api/v1/templates/",
                json={
                    "name": f"性能测试模板{time.time()}",
                    "type": "proposal",
                    "description": "性能测试用模板",
                    "content": "客户: {{ customer_name }}\n需求: {{ requirements }}"
                },
                headers=perf_benchmark.auth_headers
            )
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(create_template)
        assert single_result["success"]
        assert single_result["response_time"] < 1.0
        
        # 并发性能测试（降低并发数，因为涉及数据库写入）
        concurrent_results = perf_benchmark.run_concurrent_test(create_template, num_threads=5, requests_per_thread=3)
        
        perf_benchmark.results.append({
            "test_name": "template_creation",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言（写入操作允许更长的响应时间）
        assert concurrent_results["success_rate"] > 0.90
        assert concurrent_results["avg_response_time"] < 2.0
        assert concurrent_results["p95_response_time"] < 5.0
    
    def test_knowledge_creation_performance(self, perf_benchmark):
        """测试知识创建性能"""
        def create_knowledge():
            return perf_benchmark.client.post(
                "/api/v1/knowledge/",
                json={
                    "category": "性能测试",
                    "title": f"性能测试知识{time.time()}",
                    "content": "这是性能测试知识的详细内容",
                    "tags": ["性能", "测试"]
                },
                headers=perf_benchmark.auth_headers
            )
        
        # 单次请求性能
        single_result = perf_benchmark.measure_response_time(create_knowledge)
        assert single_result["success"]
        assert single_result["response_time"] < 1.0
        
        # 并发性能测试
        concurrent_results = perf_benchmark.run_concurrent_test(create_knowledge, num_threads=5, requests_per_thread=3)
        
        perf_benchmark.results.append({
            "test_name": "knowledge_creation",
            "single_request": single_result,
            "concurrent": concurrent_results
        })
        
        # 性能断言
        assert concurrent_results["success_rate"] > 0.90
        assert concurrent_results["avg_response_time"] < 2.0
        assert concurrent_results["p95_response_time"] < 5.0


class TestDatabasePerformance:
    """数据库性能测试"""
    
    def test_database_query_performance(self, perf_benchmark):
        """测试数据库查询性能"""
        db = TestingSessionLocal()
        
        # 测试模板查询性能
        start_time = time.time()
        templates = db.query(Template).all()
        template_query_time = time.time() - start_time
        
        # 测试知识查询性能
        start_time = time.time()
        knowledge = db.query(KnowledgeBase).all()
        knowledge_query_time = time.time() - start_time
        
        # 测试方案查询性能
        start_time = time.time()
        proposals = db.query(Proposal).all()
        proposal_query_time = time.time() - start_time
        
        db.close()
        
        # 性能断言
        assert template_query_time < 0.1  # 100ms内完成
        assert knowledge_query_time < 0.1
        assert proposal_query_time < 0.1
        
        # 验证数据量
        assert len(templates) >= 10
        assert len(knowledge) >= 20
        assert len(proposals) >= 15
    
    def test_database_insert_performance(self, perf_benchmark):
        """测试数据库插入性能"""
        db = TestingSessionLocal()
        
        # 批量插入测试
        start_time = time.time()
        for i in range(100):
            template = Template(
                name=f"批量测试模板{i}",
                type=TemplateType.PROPOSAL,
                description="批量测试用模板",
                content="测试内容"
            )
            db.add(template)
        db.commit()
        batch_insert_time = time.time() - start_time
        
        # 验证插入结果
        count = db.query(Template).filter(Template.name.like("批量测试模板%")).count()
        
        db.close()
        
        # 性能断言
        assert batch_insert_time < 2.0  # 2秒内完成100条记录插入
        assert count == 100


class TestSystemResourcePerformance:
    """系统资源性能测试"""
    
    def test_memory_usage_simulation(self, perf_benchmark):
        """模拟内存使用情况"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行一系列操作
        for i in range(50):
            response = perf_benchmark.client.get("/api/v1/templates/", headers=perf_benchmark.auth_headers)
            assert response.status_code == 200
        
        # 记录最终内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存使用断言（内存增长不应超过50MB）
        assert memory_increase < 50, f"内存增长过大: {memory_increase:.2f}MB"
    
    def test_cpu_usage_simulation(self, perf_benchmark):
        """模拟CPU使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 记录初始CPU使用率
        initial_cpu = process.cpu_percent()
        
        # 执行CPU密集操作
        start_time = time.time()
        request_count = 0
        while time.time() - start_time < 5:  # 运行5秒
            response = perf_benchmark.client.get("/api/v1/templates/", headers=perf_benchmark.auth_headers)
            if response.status_code == 200:
                request_count += 1
        
        # 记录最终CPU使用率
        final_cpu = process.cpu_percent()
        
        # 性能断言
        assert request_count > 50  # 5秒内至少完成50个请求
        assert final_cpu < 80  # CPU使用率不应超过80%


class TestPerformanceRegression:
    """性能回归测试"""
    
    def test_performance_baseline(self, perf_benchmark):
        """建立性能基线"""
        baseline_results = {}
        
        # 测试各个接口的基线性能
        endpoints = [
            ("/api/v1/templates/", "GET"),
            ("/api/v1/knowledge/", "GET"),
            ("/api/v1/proposals/", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                def make_request():
                    return perf_benchmark.client.get(endpoint, headers=perf_benchmark.auth_headers)
            else:
                def make_request():
                    return perf_benchmark.client.post(endpoint, headers=perf_benchmark.auth_headers)
            
            # 运行多次测试取平均值
            times = []
            for _ in range(10):
                result = perf_benchmark.measure_response_time(make_request)
                if result["success"]:
                    times.append(result["response_time"])
            
            if times:
                baseline_results[endpoint] = {
                    "avg_time": statistics.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "p95_time": statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times)
                }
        
        # 保存基线结果
        perf_benchmark.results.append({
            "test_name": "performance_baseline",
            "baseline": baseline_results
        })
        
        # 验证基线性能
        for endpoint, metrics in baseline_results.items():
            assert metrics["avg_time"] < 1.0, f"{endpoint} 平均响应时间过长: {metrics['avg_time']:.3f}s"
            assert metrics["p95_time"] < 2.0, f"{endpoint} P95响应时间过长: {metrics['p95_time']:.3f}s"


@pytest.mark.performance
class TestLoadTesting:
    """负载测试"""
    
    def test_sustained_load(self, perf_benchmark):
        """持续负载测试"""
        def make_request():
            return perf_benchmark.client.get("/api/v1/templates/", headers=perf_benchmark.auth_headers)
        
        # 持续1分钟的负载测试
        duration = 60  # 秒
        start_time = time.time()
        request_count = 0
        error_count = 0
        response_times = []
        
        while time.time() - start_time < duration:
            result = perf_benchmark.measure_response_time(make_request)
            request_count += 1
            if result["success"]:
                response_times.append(result["response_time"])
            else:
                error_count += 1
            
            time.sleep(0.1)  # 100ms间隔
        
        # 计算统计指标
        success_rate = (request_count - error_count) / request_count
        avg_response_time = statistics.mean(response_times) if response_times else 0
        requests_per_second = request_count / duration
        
        # 性能断言
        assert success_rate > 0.95, f"成功率过低: {success_rate:.2%}"
        assert avg_response_time < 1.0, f"平均响应时间过长: {avg_response_time:.3f}s"
        assert requests_per_second > 5, f"请求频率过低: {requests_per_second:.2f} RPS"
        
        # 记录结果
        perf_benchmark.results.append({
            "test_name": "sustained_load",
            "duration": duration,
            "total_requests": request_count,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "requests_per_second": requests_per_second
        })


def test_generate_performance_report(perf_benchmark):
    """生成性能测试报告"""
    if perf_benchmark.results:
        report = {
            "timestamp": time.time(),
            "test_results": perf_benchmark.results,
            "summary": {
                "total_tests": len(perf_benchmark.results),
                "performance_baseline_established": any("baseline" in result for result in perf_benchmark.results)
            }
        }
        
        # 这里可以将报告保存到文件或发送到监控系统
        print("性能测试报告生成完成")
        print(f"总测试数: {report['summary']['total_tests']}")
        print(f"基线建立: {report['summary']['performance_baseline_established']}")


if __name__ == "__main__":
    # 可以直接运行性能测试
    pytest.main([__file__, "-v", "-s", "--tb=short"])