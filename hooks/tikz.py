"""Подстановка отрисованных схем TikZ в страницы сайта.

Блоки ```tikz в markdown заменяются на встроенный SVG из кэша .tikz/.
SVG вставляется в страницу целиком (а не через <img>), чтобы схема
наследовала цвет текста и оставалась читаемой в тёмной теме.

Кэш наполняет tools/tikz.py (`make tikz`). Если схемы в кэше нет,
на странице появляется заметная плашка - молчаливо терять схему нельзя.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import tikz  # noqa: E402

FIGURE = (
    '<figure class="tikz-figure" markdown="0">\n'
    "{svg}\n"
    "{caption}"
    "</figure>"
)


def _caption(text):
    text = (text or "").strip()
    return f"<figcaption>{text}</figcaption>\n" if text else ""


def on_page_markdown(markdown, page, config, files, **kwargs):
    if "```tikz" not in markdown:
        return markdown

    def repl(m):
        code = m.group("code")
        digest = tikz.block_hash(code)
        path = tikz.cache_path(digest)
        if not path.exists():
            src = page.file.src_path
            print(f"WARNING - схема TikZ не отрисована: {src} "
                  f"(.tikz/{digest}.svg). Запустите `make tikz`.")
            return ('<div class="tikz-missing">Схема не отрисована: '
                    f"<code>{digest}</code>. Выполните <code>make tikz</code>.</div>")
        return FIGURE.format(
            svg=path.read_text(encoding="utf-8").strip(),
            caption=_caption(m.group("opts")),
        )

    return tikz.FENCE.sub(repl, markdown)
