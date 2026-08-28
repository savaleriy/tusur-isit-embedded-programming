#!/usr/bin/env python3
"""Сборка каталога docs/ для MkDocs из исходной структуры репозитория.

Использование:
    python3 tools/build_docs.py            # собрать docs/
    python3 tools/build_docs.py --clean    # удалить docs/
"""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Каталоги, копируемые в docs/ как есть
SOURCE_DIRS = [
    "Practice",
    "Labs",
    "Hardware",
    "Appendix",
    "Exam",
    "Students",
]

# Отдельные файлы: источник -> имя внутри docs/
SOURCE_FILES = {
    "README.md": "index.md",
}

# Что не копировать
EXCLUDE = shutil.ignore_patterns(
    "*.pyc", "__pycache__", ".obsidian", ".DS_Store", "*.tmp", "*.trash"
)

# Дополнительные ресурсы сайта, лежащие вне исходных каталогов
ASSETS_DIR = ROOT / "tools" / "assets"


MD_LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+?)((?:#[^)\s]*)?\))")


def _rewrite_links(text: str, src_file: Path, rel_dir: Path) -> str:
    """Переписывает ссылки на корневой README.md в ссылки на index.md.

    В репозитории главная страница - README.md в корне, в docs/ она
    называется index.md. Без этой замены ссылки вида ../README.md
    ломаются на сайте (MkDocs сообщает о них в строгом режиме).
    Ссылки на Labs/README.md и Hardware/README.md не трогаются:
    MkDocs считает README.md индексом каталога.
    """
    root_readme = (ROOT / "README.md").resolve()

    def repl(m):
        prefix, target, suffix = m.groups()
        if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
            return m.group(0)
        try:
            resolved = (src_file.parent / urllib.parse.unquote(target)).resolve()
        except (OSError, ValueError):
            return m.group(0)
        if resolved != root_readme:
            return m.group(0)
        depth = len(rel_dir.parts)
        new = "../" * depth + "index.md" if depth else "index.md"
        return f"{prefix}{new}{suffix}"

    return MD_LINK.sub(repl, text)


def _sync_tree(src: Path, dst: Path, prune: bool = True) -> tuple[int, int]:
    """Копирует дерево src в dst, обновляя только изменившиеся файлы.

    Возвращает (скопировано, удалено). Инкрементальность важна для
    `mkdocs serve`: без неё каждая пересборка трогает все файлы и
    вызывает бесконечный цикл перезагрузки.

    prune=True удаляет в dst то, чего больше нет в src. Для наложения
    ресурсов поверх общего каталога (tools/assets -> docs/) это нужно
    отключать, иначе будет удалено всё, чего нет в накладываемом дереве.
    """
    copied = removed = 0
    dst.mkdir(parents=True, exist_ok=True)

    src_rel = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    ignored = EXCLUDE(str(src), [p.name for p in src.rglob("*")])
    src_rel = {p for p in src_rel if not any(part in ignored for part in p.parts)}

    for rel in src_rel:
        s, d = src / rel, dst / rel
        if s.suffix == ".md":
            text = _rewrite_links(s.read_text(encoding="utf-8"), s,
                                  (dst / rel).parent.relative_to(DOCS))
            if d.exists() and d.read_text(encoding="utf-8") == text:
                continue
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_text(text, encoding="utf-8")
            copied += 1
            continue
        if d.exists() and filecmp.cmp(s, d, shallow=False):
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        copied += 1

    if not prune:
        return copied, removed

    # удалить то, чего больше нет в источнике
    for p in sorted(dst.rglob("*"), key=lambda x: -len(x.parts)):
        rel = p.relative_to(dst)
        if p.is_file() and rel not in src_rel:
            p.unlink()
            removed += 1
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()

    return copied, removed


def build(verbose: bool = True) -> None:
    if not (ROOT / "mkdocs.yml").exists():
        sys.exit("mkdocs.yml не найден - запускайте из корня репозитория")

    DOCS.mkdir(exist_ok=True)
    total_copied = total_removed = 0
    missing = []

    for name in SOURCE_DIRS:
        src = ROOT / name
        if not src.is_dir():
            missing.append(name)
            continue
        c, r = _sync_tree(src, DOCS / name)
        total_copied += c
        total_removed += r

    for src_name, dst_name in SOURCE_FILES.items():
        src = ROOT / src_name
        if not src.is_file():
            missing.append(src_name)
            continue
        dst = DOCS / dst_name
        if not (dst.exists() and filecmp.cmp(src, dst, shallow=False)):
            shutil.copy2(src, dst)
            total_copied += 1

    if ASSETS_DIR.is_dir():
        c, _ = _sync_tree(ASSETS_DIR, DOCS, prune=False)
        total_copied += c

    # убрать каталоги, оставшиеся от удалённых разделов
    known = set(SOURCE_DIRS)
    for p in DOCS.iterdir():
        if p.is_dir() and p.name not in known and p.name != "stylesheets":
            shutil.rmtree(p)
            total_removed += 1

    if verbose:
        print(f"docs/: обновлено {total_copied}, удалено {total_removed}")
    if missing:
        print(f"ВНИМАНИЕ: не найдены источники: {', '.join(missing)}", file=sys.stderr)


def clean() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
        print("docs/ удалён")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean", action="store_true", help="удалить docs/")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()
    clean() if args.clean else build(verbose=not args.quiet)
