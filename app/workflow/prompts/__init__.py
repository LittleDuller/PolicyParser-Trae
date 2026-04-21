from pathlib import PurePath

from jinja2 import Environment, FileSystemLoader

environment = Environment(
    loader=FileSystemLoader(PurePath(__file__).parent), enable_async=True
)
