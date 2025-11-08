"""文档处理服务边界测试 - 提升测试覆盖率"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.services.document_processor import DocumentProcessor


class TestDocumentProcessorBoundaryCases:
    """文档处理器边界条件测试"""

    @pytest.fixture
    def processor(self):
        """创建文档处理器实例"""
        return DocumentProcessor()

    @pytest.fixture
    def temp_files(self):
        """创建临时测试文件"""
        temp_dir = tempfile.mkdtemp()
        files = {}

        # 创建各种测试文件
        files['empty_txt'] = os.path.join(temp_dir, 'empty.txt')
        files['large_txt'] = os.path.join(temp_dir, 'large.txt')
        files['binary_file'] = os.path.join(temp_dir, 'binary.bin')
        files['corrupt_docx'] = os.path.join(temp_dir, 'corrupt.docx')
        files['corrupt_pdf'] = os.path.join(temp_dir, 'corrupt.pdf')
        files['corrupt_xlsx'] = os.path.join(temp_dir, 'corrupt.xlsx')
        files['unicode_txt'] = os.path.join(temp_dir, 'unicode.txt')
        files['special_chars_txt'] = os.path.join(temp_dir, 'special.txt')

        # 创建空文件
        open(files['empty_txt'], 'w').close()

        # 创建大文本文件 (1MB)
        with open(files['large_txt'], 'w', encoding='utf-8') as f:
            f.write("这是一行测试文本。\n" * 20000)  # 约1MB

        # 创建二进制文件
        with open(files['binary_file'], 'wb') as f:
            f.write(b'\x00\x01\x02\x03\x04\x05' * 1000)

        # 创建损坏的Office文件
        with open(files['corrupt_docx'], 'wb') as f:
            f.write(b'This is not a valid DOCX file')

        # 创建损坏的PDF文件
        with open(files['corrupt_pdf'], 'wb') as f:
            f.write(b'This is not a valid PDF file')

        # 创建损坏的Excel文件
        with open(files['corrupt_xlsx'], 'wb') as f:
            f.write(b'This is not a valid XLSX file')

        # 创建Unicode文本文件
        with open(files['unicode_txt'], 'w', encoding='utf-8') as f:
            f.write("中文测试\n")
            f.write("English Test\n")
            f.write("日本語テスト\n")
            f.write("العربية اختبار\n")
            f.write("🚀 Emoji测试 🎯\n")

        # 创建特殊字符文件
        with open(files['special_chars_txt'], 'w', encoding='utf-8') as f:
            f.write("特殊字符测试:\n")
            f.write("引号: \"双引号\" 和 '单引号'\n")
            f.write("符号: @#$%^&*()_+-=[]{}|;':\",./<>?\n")
            f.write("转义: \\n \\t \\r \\x00\n")
            f.write("HTML: <div>content</div>\n")
            f.write("XML: <?xml version=\"1.0\"?><root>data</root>\n")

        yield files

        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)

    # ========== 空文件和边界文件测试 ==========

    def test_extract_text_from_empty_file(self, processor, temp_files):
        """测试空文件处理"""
        result = processor.extract_text_from_txt(temp_files['empty_txt'])
        assert result == ""

    def test_extract_text_from_nonexistent_file(self, processor):
        """测试不存在的文件"""
        with pytest.raises(FileNotFoundError):
            processor.extract_text_from_txt("/path/to/nonexistent/file.txt")

    def test_extract_text_from_binary_file(self, processor, temp_files):
        """测试二进制文件处理"""
        # 二进制文件应该返回空字符串或抛出异常
        result = processor.extract_text_from_txt(temp_files['binary_file'])
        # 由于编码问题，可能返回空字符串或乱码
        assert isinstance(result, str)

    # ========== 编码和字符集边界测试 ==========

    def test_extract_text_unicode_content(self, processor, temp_files):
        """测试Unicode内容提取"""
        result = processor.extract_text_from_txt(temp_files['unicode_txt'])

        assert "中文测试" in result
        assert "English Test" in result
        assert "日本語テスト" in result
        assert "العربية اختبار" in result
        assert "🚀" in result
        assert "🎯" in result

    def test_extract_text_special_characters(self, processor, temp_files):
        """测试特殊字符处理"""
        result = processor.extract_text_from_txt(temp_files['special_chars_txt'])

        assert "特殊字符测试" in result
        assert '"双引号"' in result
        assert "'单引号'" in result
        assert "@#$%^&*()" in result
        assert "\\n \\t \\r \\x00" in result
        assert "<div>content</div>" in result
        assert "<?xml version=\"1.0\"?><root>data</root>" in result

    def test_extract_text_different_encodings(self, processor):
        """测试不同编码格式的文本文件"""
        temp_dir = tempfile.mkdtemp()

        try:
            # UTF-8编码
            utf8_file = os.path.join(temp_dir, 'utf8.txt')
            with open(utf8_file, 'w', encoding='utf-8') as f:
                f.write("UTF-8编码测试: 中文English日本語")

            result = processor.extract_text_from_txt(utf8_file)
            assert "UTF-8编码测试" in result
            assert "中文" in result
            assert "English" in result
            assert "日本語" in result

            # GBK编码（中文）
            gbk_file = os.path.join(temp_dir, 'gbk.txt')
            with open(gbk_file, 'w', encoding='gbk') as f:
                f.write("GBK编码测试: 中文内容")

            result = processor.extract_text_from_txt(gbk_file)
            # 应该能正确处理GBK编码
            assert isinstance(result, str)

            # Latin-1编码
            latin_file = os.path.join(temp_dir, 'latin.txt')
            with open(latin_file, 'w', encoding='latin-1') as f:
                f.write("Latin-1 encoding test: café, naïve, résumé")

            result = processor.extract_text_from_txt(latin_file)
            assert "Latin-1" in result
            assert "café" in result
            assert "naïve" in result
            assert "résumé" in result

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 文件大小边界测试 ==========

    def test_extract_text_large_file(self, processor, temp_files):
        """测试大文件处理"""
        result = processor.extract_text_from_txt(temp_files['large_txt'])

        # 验证文件大小
        assert len(result) > 100000  # 应该超过10万字
        assert "这是一行测试文本。" in result
        assert result.count("这是一行测试文本。") == 20000

    def test_extract_text_very_long_single_line(self, processor):
        """测试超长的单行文本"""
        temp_dir = tempfile.mkdtemp()

        try:
            long_line_file = os.path.join(temp_dir, 'long_line.txt')
            # 创建一行10万个字符的文本
            long_line = "这是一个超长的测试行，" * 20000

            with open(long_line_file, 'w', encoding='utf-8') as f:
                f.write(long_line)

            result = processor.extract_text_from_txt(long_line_file)
            assert len(result) > 100000
            assert "这是一个超长的测试行，" in result

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 损坏文件处理测试 ==========

    def test_extract_text_from_corrupt_docx(self, processor, temp_files):
        """测试损坏的Word文档"""
        with pytest.raises(Exception) as exc_info:
            processor.extract_text_from_docx(temp_files['corrupt_docx'])

        # 应该抛出文档格式相关的异常
        assert "docx" in str(exc_info.value).lower() or "document" in str(exc_info.value).lower()

    def test_extract_text_from_corrupt_pdf(self, processor, temp_files):
        """测试损坏的PDF文档"""
        with pytest.raises(Exception) as exc_info:
            processor.extract_text_from_pdf(temp_files['corrupt_pdf'])

        # 应该抛出PDF格式相关的异常
        assert "pdf" in str(exc_info.value).lower() or "document" in str(exc_info.value).lower()

    def test_extract_text_from_corrupt_xlsx(self, processor, temp_files):
        """测试损坏的Excel文档"""
        with pytest.raises(Exception) as exc_info:
            processor.extract_text_from_xlsx(temp_files['corrupt_xlsx'])

        # 应该抛出Excel格式相关的异常
        assert "xlsx" in str(exc_info.value).lower() or "excel" in str(exc_info.value).lower()

    # ========== 文件权限和路径测试 ==========

    def test_extract_text_no_read_permission(self, processor):
        """测试没有读取权限的文件"""
        temp_dir = tempfile.mkdtemp()

        try:
            no_permission_file = os.path.join(temp_dir, 'no_permission.txt')
            with open(no_permission_file, 'w') as f:
                f.write("测试内容")

            # 移除读取权限（在Unix系统上）
            if os.name != 'nt':  # 非Windows系统
                os.chmod(no_permission_file, 0o000)

                with pytest.raises(PermissionError):
                    processor.extract_text_from_txt(no_permission_file)

                # 恢复权限以便清理
                os.chmod(no_permission_file, 0o644)

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    def test_extract_text_special_file_paths(self, processor):
        """测试特殊文件路径"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 包含空格的路径
            space_file = os.path.join(temp_dir, 'file with spaces.txt')
            with open(space_file, 'w', encoding='utf-8') as f:
                f.write("包含空格的文件路径测试")

            result = processor.extract_text_from_txt(space_file)
            assert "包含空格的文件路径测试" in result

            # 包含特殊字符的路径
            special_file = os.path.join(temp_dir, 'file-with_special.chars.txt')
            with open(special_file, 'w', encoding='utf-8') as f:
                f.write("特殊字符文件名测试")

            result = processor.extract_text_from_txt(special_file)
            assert "特殊字符文件名测试" in result

            # 很长的文件名
            long_name = "a" * 200 + ".txt"
            long_file = os.path.join(temp_dir, long_name)
            with open(long_file, 'w', encoding='utf-8') as f:
                f.write("长文件名测试")

            result = processor.extract_text_from_txt(long_file)
            assert "长文件名测试" in result

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 文档格式变异测试 ==========

    def test_extract_text_malformed_txt_content(self, processor):
        """测试格式不规范的文本内容"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 混合编码内容
            mixed_file = os.path.join(temp_dir, 'mixed.txt')
            with open(mixed_file, 'wb') as f:
                f.write(b'Valid text\n')
                f.write(b'\xff\xfe\x00\x00')  # 无效字节序列
                f.write(b'More text\n')

            # 应该能处理或跳过无效部分
            result = processor.extract_text_from_txt(mixed_file)
            assert isinstance(result, str)

            # 二进制伪装成文本
            binary_text_file = os.path.join(temp_dir, 'binary_text.txt')
            with open(binary_text_file, 'wb') as f:
                f.write(b'Text start\x00\x01\x02\x03\x04Text end')

            result = processor.extract_text_from_txt(binary_text_file)
            assert isinstance(result, str)

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 并发和性能测试 ==========

    def test_extract_text_multiple_files_concurrently(self, processor, temp_files):
        """测试并发文件处理"""
        import threading
        import time

        results = {}
        errors = {}

        def extract_file(file_key, file_path):
            try:
                start_time = time.time()
                result = processor.extract_text_from_txt(file_path)
                end_time = time.time()
                results[file_key] = {
                    'content': result,
                    'time': end_time - start_time,
                    'size': os.path.getsize(file_path)
                }
            except Exception as e:
                errors[file_key] = str(e)

        # 启动多个线程处理不同文件
        threads = []
        for key, path in temp_files.items():
            if key.endswith('_txt'):
                thread = threading.Thread(target=extract_file, args=(key, path))
                threads.append(thread)
                thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) > 0
        assert len(errors) == 0  # 不应该有错误

        # 验证Unicode文件内容
        if 'unicode_txt' in results:
            assert "中文测试" in results['unicode_txt']['content']
            assert "English Test" in results['unicode_txt']['content']

    def test_extract_text_performance_large_file(self, processor, temp_files):
        """测试大文件处理性能"""
        import time

        # 测试大文件处理时间
        start_time = time.time()
        result = processor.extract_text_from_txt(temp_files['large_txt'])
        end_time = time.time()

        processing_time = end_time - start_time
        file_size = os.path.getsize(temp_files['large_txt'])

        # 验证结果
        assert len(result) > 0
        assert "这是一行测试文本。" in result

        # 性能应该在合理范围内（10MB文件应该在5秒内处理完成）
        assert processing_time < 5.0, f"大文件处理时间过长: {processing_time}秒"

        # 计算处理速度
        processing_speed = file_size / processing_time / 1024 / 1024  # MB/s
        print(f"文件处理速度: {processing_speed:.2f} MB/s")

    # ========== 错误恢复和容错测试 ==========

    def test_extract_text_error_recovery(self, processor):
        """测试错误恢复机制"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建一个部分损坏的文件
            partial_file = os.path.join(temp_dir, 'partial.txt')
            with open(partial_file, 'w', encoding='utf-8') as f:
                f.write("正常文本内容\n")
                f.write("更多正常内容\n")

            # 模拟文件在读取过程中被损坏
            original_open = open

            def mock_open(filename, mode='r', **kwargs):
                if filename == partial_file and mode == 'r':
                    # 返回一个会在读取中出错的文件对象
                    class ErrorFile:
                        def __init__(self):
                            self.lines = ["正常文本内容\n", "更多正常内容\n"]
                            self.index = 0

                        def read(self, size=-1):
                            if self.index < len(self.lines):
                                line = self.lines[self.index]
                                self.index += 1
                                return line
                            return ""

                        def __iter__(self):
                            return self

                        def __next__(self):
                            if self.index < len(self.lines):
                                line = self.lines[self.index]
                                self.index += 1
                                return line
                            raise StopIteration

                        def close(self):
                            pass

                        def __enter__(self):
                            return self

                        def __exit__(self, *args):
                            pass

                    return ErrorFile()
                return original_open(filename, mode, **kwargs)

            with patch('builtins.open', mock_open):
                result = processor.extract_text_from_txt(partial_file)
                assert "正常文本内容" in result
                assert "更多正常内容" in result

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 文档类型边界测试 ==========

    def test_extract_text_unsupported_file_type(self, processor):
        """测试不支持的文件类型"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建不支持的文件类型
            unsupported_file = os.path.join(temp_dir, 'unsupported.xyz')
            with open(unsupported_file, 'w') as f:
                f.write("Some content")

            # 应该抛出文件类型不支持的错误
            with pytest.raises(ValueError, match="不支持"):
                processor.extract_text_from_docx(unsupported_file)

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    def test_extract_text_zero_byte_file(self, processor):
        """测试零字节文件"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建零字节文件
            zero_file = os.path.join(temp_dir, 'zero.txt')
            # 创建文件但不写入任何内容
            open(zero_file, 'w').close()

            result = processor.extract_text_from_txt(zero_file)
            assert result == ""
            assert len(result) == 0

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 路径遍历和安全测试 ==========

    def test_extract_text_path_traversal_protection(self, processor):
        """测试路径遍历攻击防护"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建测试文件
            test_file = os.path.join(temp_dir, 'safe.txt')
            with open(test_file, 'w') as f:
                f.write("Safe content")

            # 尝试路径遍历
            malicious_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "../../sensitive.txt",
                "/etc/shadow",
                "C:\\Windows\\System32\\config\\SAM"
            ]

            for malicious_path in malicious_paths:
                # 应该抛出文件不存在的错误，而不是访问系统文件
                with pytest.raises(FileNotFoundError):
                    processor.extract_text_from_txt(malicious_path)

        finally:
            import shutil
            shutil.rmtree(temp_dir)

    # ========== 内存压力测试 ==========

    def test_extract_text_memory_efficiency(self, processor):
        """测试内存效率"""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # 获取初始内存使用
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        temp_dir = tempfile.mkdtemp()

        try:
            # 创建一系列文件进行处理
            files = []
            for i in range(10):
                file_path = os.path.join(temp_dir, f'test_{i}.txt')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"文件{i}内容\n" * 1000)  # 每个文件约20KB
                files.append(file_path)

            # 处理所有文件
            results = []
            for file_path in files:
                result = processor.extract_text_from_txt(file_path)
                results.append(result)

            # 获取处理后内存使用
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB

            # 验证结果
            assert len(results) == 10
            for i, result in enumerate(results):
                assert f"文件{i}内容" in result

            # 内存增长应该在合理范围内（假设增长不超过100MB）
            memory_growth = final_memory - initial_memory
            assert memory_growth < 100, f"内存增长过大: {memory_growth}MB"

        finally:
            import shutil
            shutil.rmtree(temp_dir)