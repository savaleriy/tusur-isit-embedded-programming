#!/usr/bin/env python3
"""Рендеринг блоков TikZ из markdown в SVG.

Использование
-------------
    python3 tools/tikz.py            # отрендерить всё, чего нет в кэше
    python3 tools/tikz.py --force    # перерисовать всё заново
    python3 tools/tikz.py --check    # только проверить полноту кэша
    python3 tools/tikz.py --prune    # удалить из кэша лишнее
    python3 tools/tikz.py --png      # дополнительно растр для DOCX
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".tikz"
STYLES = ROOT / "tools" / "tex" / "course.tikzstyles.tex"

SKIP_DIRS = {".git", ".obsidian", "old_materials", "_archive", "site", "docs",
             "__pycache__", ".venv", ".tikz", "node_modules"}

# ```tikz ... ``` с необязательным заголовком после языка
FENCE = re.compile(
    r"^(?P<indent>[ \t]*)```tikz(?P<opts>[^\n]*)\n(?P<code>.*?)^(?P=indent)```[ \t]*$",
    re.M | re.S,
)

PREAMBLE = r"""\documentclass[border=6pt,tikz]{standalone}
\usepackage{fontspec}
\setmainfont{DejaVu Sans}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
\usepackage{amsmath}
\usepackage{unicode-math}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{
  arrows.meta, positioning, calc, patterns, patterns.meta, decorations.pathreplacing,
  decorations.markings, decorations.pathmorphing, shapes.geometric, shapes.misc,
  fit, backgrounds, matrix, chains, intersections, plotmarks, spy
}
"""

# Палитра курса: одинаковая во всех схемах, различима в обеих темах
COLORS = r"""\definecolor{sig}{HTML}{1E88A8}
\definecolor{clk}{HTML}{B8571A}
\definecolor{acc}{HTML}{C2185B}
\definecolor{ok}{HTML}{2E7D32}
\definecolor{warn}{HTML}{C62828}
\definecolor{muted}{HTML}{78909C}
"""


def load_styles() -> str:
    """Библиотека стилей курса, общая для всех схем.

    Держать её отдельным файлом, а не внутри этого модуля, удобно по двум
    причинам: файл подсвечивается как LaTeX и его можно подключить в
    Obsidian, чтобы схемы там выглядели так же, как на сайте.
    """
    return STYLES.read_text(encoding="utf-8") if STYLES.exists() else ""


class TikzError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Разбор исходников
# --------------------------------------------------------------------------

def iter_markdown(base: Path = ROOT):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".md"):
                yield Path(root) / f


def normalize(code: str) -> tuple[list[str], str]:
    """Приводит блок к виду (список \\usepackage, тело картинки).

    Поддерживаются обе формы записи: как в Obsidian (с \\usepackage и
    \\begin{document}) и голая - сразу \\begin{tikzpicture}.
    """
    packages = re.findall(r"^\s*(\\usepackage(?:\[[^\]]*\])?\{[^}]+\})\s*$",
                          code, re.M)
    libs = re.findall(r"^\s*(\\usetikzlibrary\{[^}]+\})\s*$", code, re.M)
    defs = re.findall(r"^\s*(\\definecolor\{[^}]+\}\{[^}]+\}\{[^}]+\})\s*$",
                      code, re.M)

    m = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", code, re.S)
    body = m.group(1) if m else code
    # убрать директивы преамбулы из тела
    body = re.sub(r"^\s*\\usepackage(?:\[[^\]]*\])?\{[^}]+\}\s*$", "", body, flags=re.M)
    body = re.sub(r"^\s*\\usetikzlibrary\{[^}]+\}\s*$", "", body, flags=re.M)
    return packages + libs + defs, body.strip()


def block_hash(code: str) -> str:
    """Ключ кэша. В хэш входит преамбула: её правка перерисует все схемы."""
    h = hashlib.sha256()
    h.update(PREAMBLE.encode())
    h.update(COLORS.encode())
    h.update(load_styles().encode())
    h.update(code.strip().encode())
    return h.hexdigest()[:16]


def collect_blocks() -> list[tuple[Path, int, str, str]]:
    """Все блоки tikz в репозитории: (файл, номер строки, код, хэш)."""
    out = []
    for p in iter_markdown():
        text = p.read_text(encoding="utf-8")
        for m in FENCE.finditer(text):
            code = m.group("code")
            lineno = text[: m.start()].count("\n") + 1
            out.append((p, lineno, code, block_hash(code)))
    return out


# --------------------------------------------------------------------------
# Рендеринг
# --------------------------------------------------------------------------

def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_toolchain() -> list[str]:
    missing = []
    if not _have("dvilualatex") and not _have("lualatex"):
        missing.append("dvilualatex (пакет texlive-luatex)")
    if not _have("dvisvgm"):
        missing.append("dvisvgm (пакет texlive-binextra)")
    return missing


def postprocess(svg: str) -> str:
    """Готовит SVG к встраиванию в страницу.

    - чёрный цвет заменяется на currentColor (работа в тёмной теме);
    - фиксированные размеры в pt заменяются на масштабируемые;
    - убирается XML-заголовок, мешающий встраиванию.
    """
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)

    for attr in ("stroke", "fill"):
        svg = re.sub(rf"{attr}='#0{{3,6}}'", f"{attr}='currentColor'", svg)
        svg = re.sub(rf'{attr}="#0{{3,6}}"', f'{attr}="currentColor"', svg)

    m = re.search(r"<svg([^>]*)>", svg)
    if not m:
        raise TikzError("dvisvgm вернул не SVG")
    attrs = m.group(1)
    wm = re.search(r"width='([\d.]+)pt'", attrs)
    width_pt = float(wm.group(1)) if wm else 400.0

    new_attrs = re.sub(r"\s(width|height)='[^']*'", "", attrs)
    # max-width в px не даёт схеме растянуться сверх её натурального размера,
    # width:100% - сжимает её на узком экране
    new_attrs += (
        " fill='currentColor'"
        " class='tikz'"
        f" style='width:100%;max-width:{width_pt * 1.34:.0f}px;height:auto'"
    )
    return svg.replace(m.group(0), f"<svg{new_attrs}>", 1)


def render(code: str, keep_log: bool = False) -> str:
    packages, body = normalize(code)
    doc = PREAMBLE + "\n".join(packages) + "\n" + COLORS + load_styles() + \
        "\\begin{document}\n" + body + "\n\\end{document}\n"

    with tempfile.TemporaryDirectory(prefix="tikz-") as tmp:
        tmp = Path(tmp)
        tex = tmp / "fig.tex"
        tex.write_text(doc, encoding="utf-8")

        latex = "dvilualatex" if _have("dvilualatex") else "lualatex"
        proc = subprocess.run(
            [latex, "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={tmp}", str(tex)],
            capture_output=True, text=True, cwd=tmp, timeout=120,
        )
        dvi = tmp / "fig.dvi"
        if proc.returncode != 0 or not dvi.exists():
            log = (tmp / "fig.log")
            detail = ""
            if log.exists():
                lines = log.read_text(encoding="utf-8", errors="replace").split("\n")
                errs = [l for l in lines if l.startswith("!") or "Error" in l]
                detail = "\n".join(errs[:6]) or "\n".join(lines[-12:])
            raise TikzError(f"LaTeX не собрал схему:\n{detail}")

        svg_path = tmp / "fig.svg"
        proc = subprocess.run(
            ["dvisvgm", "--no-fonts", "--exact-bbox", "--scale=1.35",
             "-o", str(svg_path), str(dvi)],
            capture_output=True, text=True, timeout=120,
        )
        if not svg_path.exists():
            raise TikzError(f"dvisvgm не создал SVG:\n{proc.stderr[-500:]}")

        return postprocess(svg_path.read_text(encoding="utf-8"))


def render_png(code: str, dpi: int = 200) -> bytes:
    """Растровая версия схемы для DOCX.

    Pandoc не умеет вставлять SVG в docx без librsvg, поэтому для
    конспекта в Word схемы дополнительно рендерятся в PNG:
    lualatex -> PDF -> pdftocairo -> PNG.
    """
    packages, body = normalize(code)
    doc = PREAMBLE + "\n".join(packages) + "\n" + COLORS + load_styles() + \
        "\\begin{document}\n" + body + "\n\\end{document}\n"

    with tempfile.TemporaryDirectory(prefix="tikz-png-") as tmp:
        tmp = Path(tmp)
        tex = tmp / "fig.tex"
        tex.write_text(doc, encoding="utf-8")

        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={tmp}", str(tex)],
            capture_output=True, text=True, cwd=tmp, timeout=120,
        )
        pdf = tmp / "fig.pdf"
        if proc.returncode != 0 or not pdf.exists():
            raise TikzError("lualatex не собрал PDF для растра")

        subprocess.run(
            ["pdftocairo", "-png", "-r", str(dpi), "-singlefile",
             str(pdf), str(tmp / "fig")],
            capture_output=True, timeout=120,
        )
        png = tmp / "fig.png"
        if not png.exists():
            raise TikzError("pdftocairo не создал PNG")
        return png.read_bytes()


def cache_path(digest: str) -> Path:
    return CACHE / f"{digest}.svg"


def cache_path_png(digest: str) -> Path:
    return CACHE / f"{digest}.png"


def build(force: bool = False, prune: bool = False, png: bool = False) -> int:
    blocks = collect_blocks()
    if not blocks:
        print("Блоков ```tikz не найдено")
        return 0

    missing_tools = check_toolchain()
    todo = [b for b in blocks if force or not cache_path(b[3]).exists()]
    todo_png = [b for b in blocks
                if png and (force or not cache_path_png(b[3]).exists())]

    if (todo or todo_png) and missing_tools:
        print("Для рендеринга схем нужны: " + ", ".join(missing_tools), file=sys.stderr)
        print(f"Не хватает {len(todo)} схем в кэше .tikz/", file=sys.stderr)
        return 1

    CACHE.mkdir(exist_ok=True)
    errors = 0
    for path, lineno, code, digest in todo:
        rel = path.relative_to(ROOT)
        try:
            svg = render(code)
        except (TikzError, subprocess.TimeoutExpired) as e:
            print(f"  [ОШИБКА] {rel}:{lineno}\n{e}", file=sys.stderr)
            errors += 1
            continue
        cache_path(digest).write_text(svg, encoding="utf-8")
        size = len(svg) // 1024
        print(f"  [ок] {rel}:{lineno} -> .tikz/{digest}.svg ({size} КБ)")

    for path, lineno, code, digest in todo_png:
        rel = path.relative_to(ROOT)
        try:
            data = render_png(code)
        except (TikzError, subprocess.TimeoutExpired) as e:
            print(f"  [ОШИБКА PNG] {rel}:{lineno}: {e}", file=sys.stderr)
            errors += 1
            continue
        cache_path_png(digest).write_bytes(data)
        print(f"  [ок] {rel}:{lineno} -> .tikz/{digest}.png ({len(data) // 1024} КБ)")

    if not todo and not todo_png:
        print(f"Все {len(blocks)} схем уже в кэше")

    if prune:
        used = {b[3] for b in blocks}
        for f in list(CACHE.glob("*.svg")) + list(CACHE.glob("*.png")):
            if f.stem not in used:
                f.unlink()
                print(f"  удалён неиспользуемый {f.name}")

    if errors:
        print(f"\nНе отрисовано схем: {errors}", file=sys.stderr)
    return 1 if errors else 0


def check() -> int:
    """Проверяет, что для каждого блока есть готовый SVG."""
    blocks = collect_blocks()
    missing = [(p, ln, d) for p, ln, _, d in blocks if not cache_path(d).exists()]
    if not blocks:
        print("  [ок]     схемы TikZ: блоков нет")
        return 0
    if missing:
        print(f"  [ОШИБКА] схемы TikZ: не отрисовано {len(missing)} из {len(blocks)}")
        for p, ln, d in missing[:10]:
            print(f"           {p.relative_to(ROOT)}:{ln} (нет .tikz/{d}.svg)")
        print("           запустите: make tikz")
        return 1
    print(f"  [ок]     схемы TikZ: {len(blocks)} блоков, все отрисованы")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="перерисовать всё")
    ap.add_argument("--check", action="store_true", help="только проверить кэш")
    ap.add_argument("--prune", action="store_true", help="удалить лишнее из кэша")
    ap.add_argument("--png", action="store_true",
                    help="дополнительно отрисовать растр для DOCX")
    a = ap.parse_args()
    sys.exit(check() if a.check
             else build(force=a.force, prune=a.prune, png=a.png))
