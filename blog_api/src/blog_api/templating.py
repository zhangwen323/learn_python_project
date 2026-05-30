"""Shared Jinja2Templates instance — avoids circular imports between main.py and pages.py."""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")), cache_size=0)
templates = Jinja2Templates(env=env)
