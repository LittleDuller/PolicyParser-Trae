import pytest

from app.utils import html_to_markdown
from tests.utils import get_policy_source_path


@pytest.mark.parametrize("file_path", get_policy_source_path())
def test(file_path, read_file):
    policy_source = read_file(file_path)

    policy_content = html_to_markdown(policy_source)

    # 确保返回结果是一个非空的字符串
    assert policy_content is not None
    assert isinstance(policy_content, str)
    assert len(policy_content.strip()) > 0

    # 确保没有残留大块的未解析代码
    html_tags = ["<html", "<body", "<div", "<span", "<script", "<style", "<p"]
    for tag in html_tags:
        assert tag not in policy_content.lower(), (
            f"提取失败，结果中仍包含原始 HTML 标签: {tag}"
        )

    print(f"\n[{file_path}] 提取成功，内容长度: {len(policy_content)}")
    print(policy_content)


class TestHtmlParserEdgeCases:
    """边界条件测试类"""

    def test_empty_html_input(self):
        """测试空 HTML 输入"""
        result = html_to_markdown("")
        assert result is not None
        assert isinstance(result, str)

    def test_empty_html_input_with_spaces(self):
        """测试只包含空格的 HTML 输入"""
        result = html_to_markdown("   ")
        assert result is not None
        assert isinstance(result, str)

    def test_plain_text_input(self):
        """测试纯文本输入 (无 HTML 标签)"""
        text = "这是纯文本"
        result = html_to_markdown(text)
        assert result is not None
        assert isinstance(result, str)
        assert "这是纯文本" in result

    def test_plain_text_with_line_breaks(self):
        """测试带换行的纯文本输入"""
        text = "第一行\n第二行\n第三行"
        result = html_to_markdown(text)
        assert result is not None
        assert isinstance(result, str)
        assert "第一行" in result
        assert "第二行" in result
        assert "第三行" in result

    def test_special_characters_ampersand(self):
        """测试特殊字符处理 - & 符号"""
        text = "测试 & 符号"
        result = html_to_markdown(text)
        assert result is not None
        assert isinstance(result, str)
        assert "测试" in result
        assert "符号" in result

    def test_special_characters_less_greater(self):
        """测试特殊字符处理 - < 和 > 符号"""
        text = "a < b > c"
        result = html_to_markdown(text)
        assert result is not None
        assert isinstance(result, str)

    def test_nested_html_tags(self):
        """测试嵌套 HTML 标签"""
        html = "<div><p>嵌套内容</p></div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "嵌套内容" in result
        assert "<div" not in result.lower()
        assert "<p" not in result.lower()

    def test_deeply_nested_html_tags(self):
        """测试深层嵌套 HTML 标签"""
        html = "<div><span><strong><em>深层嵌套内容</em></strong></span></div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "深层嵌套内容" in result

    def test_empty_html_tags(self):
        """测试只有 HTML 标签没有内容"""
        html = "<div></div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "<div" not in result.lower()

    def test_multiple_empty_html_tags(self):
        """测试多个空 HTML 标签"""
        html = "<div></div><p></p><span></span>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "<div" not in result.lower()
        assert "<p" not in result.lower()
        assert "<span" not in result.lower()

    def test_html_tags_with_only_whitespace(self):
        """测试 HTML 标签内只有空白字符"""
        html = "<div>   </div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)

    def test_mixed_content(self):
        """测试混合内容 - 标签和文本混合"""
        html = "<div>前<p>中间</p>后</div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "前" in result
        assert "中间" in result
        assert "后" in result

    def test_none_input(self):
        """测试 None 输入"""
        with pytest.raises(Exception):
            html_to_markdown(None)

    def test_html_with_comments(self):
        """测试包含 HTML 注释的内容"""
        html = "<div>正文<!-- 这是注释 --></div>"
        result = html_to_markdown(html)
        assert result is not None
        assert isinstance(result, str)
        assert "正文" in result
        assert "<!--" not in result
        assert "-->" not in result
