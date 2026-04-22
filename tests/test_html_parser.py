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
