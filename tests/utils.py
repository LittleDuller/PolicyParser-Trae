import os
from pathlib import PurePath
from turtle import st


def get_policy_source_path():
    """
    获取政策原文文件路径列表
    """
    path = PurePath(__file__).parent.joinpath("policies")
    files = []
    for file in os.scandir(path):
        if (
            file.is_file()
            and file.name.startswith("policy")
            and file.name.endswith("source.txt")
        ):
            files.append(file.path)
    return files


def get_policy_content_path(pattern: str | None = None):
    """
    获取政策解析后文件路径列表
    Args:
        idx: 只看编号为 idx 的wen
    """
    path = PurePath(__file__).parent.joinpath("policies")
    files = []
    for file in os.scandir(path):
        if (
            file.is_file()
            and file.name.startswith("policy")
            and file.name.endswith("content.txt")
        ):
            if pattern is None or pattern in file.name:
                files.append(file.path)
    return files
