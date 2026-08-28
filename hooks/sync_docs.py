"""Пересборка docs/ перед каждой сборкой сайта.

Материалы курса лежат в корне репозитория; docs/ - генерируемая копия.
Этот хук вызывается MkDocs на старте сборки, поэтому `mkdocs serve`
подхватывает правки в исходных файлах: watch (см. mkdocs.yml) замечает
изменение, MkDocs пересобирается, хук синхронизирует docs/.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_docs  # noqa: E402


def on_config(config, **kwargs):
    build_docs.build(verbose=False)
    return config
