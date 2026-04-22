import re

from markdownify import markdownify as md

PATTERN_NEWLINES = re.compile(r'\n{3,}')


def html_to_markdown(html):
    markdown = md(html)
    markdown = PATTERN_NEWLINES.sub('\n\n', markdown)  # 去除多余的连续换行符
    return markdown
