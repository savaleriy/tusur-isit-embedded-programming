#!/usr/bin/env python3
"""Проверка материалов курса и собранного сайта до публикации.

Коды возврата: 0 - всё хорошо, 1 - есть ошибки.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

SOURCE_DIRS = ["Practice", "Labs", "Hardware", "Appendix", "Exam", "Students"]
SKIP_DIRS = {".git", ".obsidian", "_archive", "old_materials", "site", "docs",
             "__pycache__", ".venv", "node_modules"}

# Кириллица + базовый ASCII. Правило курса: никаких типографских тире,
# "ёлочек", стрелок и псевдографики Unicode - только LaTeX для формул.
CYRILLIC = range(0x400, 0x500)

MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:", "#", "javascript:")


def site_base() -> str:
    """Префикс пути из site_url: сайт публикуется не в корне домена,
    поэтому абсолютные ссылки в HTML начинаются с /<repo>/."""
    cfg = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    m = re.search(r"^site_url:\s*(\S+)", cfg, re.M)
    if not m:
        return ""
    path = urllib.parse.urlparse(m.group(1)).path
    return path.rstrip("/")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks = 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def section(self, name: str, problems: list[str], warn_only: bool = False) -> None:
        self.checks += 1
        if not problems:
            print(f"  [ок]     {name}")
            return
        mark = "[преду]" if warn_only else "[ОШИБКА]"
        print(f"  {mark} {name}: {len(problems)}")
        for p in problems[:15]:
            print(f"           {p}")
        if len(problems) > 15:
            print(f"           ... и ещё {len(problems) - 15}")
        (self.warnings if warn_only else self.errors).extend(problems)


def iter_markdown(base: Path):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".md"):
                yield Path(root) / f


# --------------------------------------------------------------------------
# Проверки исходников
# --------------------------------------------------------------------------

def check_charset() -> list[str]:
    """Только ASCII и кириллица - правило оформления курса."""
    bad = []
    for p in iter_markdown(ROOT):
        text = p.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.split("\n"), 1):
            for ch in line:
                o = ord(ch)
                if o < 128 or o in CYRILLIC:
                    continue
                rel = p.relative_to(ROOT)
                bad.append(f"{rel}:{lineno}: символ {ch!r} (U+{o:04X})")
                break
    return bad


def check_source_links() -> list[str]:
    """Относительные ссылки и картинки указывают на существующие файлы."""
    bad = []
    for p in iter_markdown(ROOT):
        text = p.read_text(encoding="utf-8")
        for m in MD_LINK.finditer(text):
            target = m.group(1)
            if target.startswith(EXTERNAL):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            resolved = (p.parent / urllib.parse.unquote(target)).resolve()
            if not resolved.exists():
                lineno = text[: m.start()].count("\n") + 1
                bad.append(f"{p.relative_to(ROOT)}:{lineno}: -> {target}")
    return bad


def load_nav() -> tuple[list[str], list[str]]:
    """Возвращает (пути из nav, ошибки разбора). YAML читаем построчно,
    чтобы не тянуть PyYAML и не спотыкаться о теги !!python/name."""
    cfg = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    if "\nnav:" not in cfg:
        return [], ["в mkdocs.yml нет раздела nav"]
    nav_block = cfg.split("\nnav:", 1)[1]
    paths = []
    for line in nav_block.split("\n"):
        if line and not line[0].isspace() and line.strip():
            break  # начался следующий раздел верхнего уровня
        m = re.search(r":\s*([^\s:][^:]*\.md)\s*$", line)
        if m:
            paths.append(m.group(1).strip())
        elif re.match(r"\s*-\s+([^\s:][^:]*\.md)\s*$", line):
            paths.append(re.match(r"\s*-\s+(.*\.md)\s*$", line).group(1).strip())
    return paths, []


def check_nav(nav_paths: list[str]) -> tuple[list[str], list[str]]:
    """Все пункты nav существуют; все материалы попали в nav."""
    missing = []
    docs = ROOT / "docs"
    for rel in nav_paths:
        # index.md собирается из README.md
        src = ROOT / "README.md" if rel == "index.md" else ROOT / rel
        if not src.exists() and not (docs / rel).exists():
            missing.append(f"nav -> {rel} (файла нет)")

    in_nav = set(nav_paths)
    orphans = []
    for d in SOURCE_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in iter_markdown(base):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in in_nav:
                orphans.append(f"{rel} (нет в nav - страница будет недоступна)")
    return missing, orphans


def check_lesson_numbering() -> list[str]:
    """Номер в заголовке и в номерах задач совпадает с номером каталога."""
    bad = []
    practice = ROOT / "Practice"
    if not practice.is_dir():
        return ["нет каталога Practice/"]
    for d in sorted(practice.iterdir()):
        if not d.is_dir():
            continue
        m = re.match(r"(\d+)-", d.name)
        if not m:
            bad.append(f"{d.name}: имя каталога не начинается с номера")
            continue
        num = int(m.group(1))
        note, task = d / "note.md", d / "task.md"
        if not note.exists():
            bad.append(f"{d.name}: нет note.md")
        else:
            h = note.read_text(encoding="utf-8").split("\n", 1)[0]
            hm = re.search(r"Занятие\s+(\d+)", h)
            if not hm:
                bad.append(f"{d.name}/note.md: в заголовке нет номера занятия")
            elif int(hm.group(1)) != num:
                bad.append(f"{d.name}/note.md: заголовок 'Занятие {hm.group(1)}'")
        if not task.exists():
            bad.append(f"{d.name}: нет task.md")
        else:
            tm = re.search(r"^## (\d+)\.\d+\.", task.read_text(encoding="utf-8"), re.M)
            if not tm:
                bad.append(f"{d.name}/task.md: нет задач вида '## N.M.'")
            elif int(tm.group(1)) != num:
                bad.append(f"{d.name}/task.md: задачи пронумерованы как {tm.group(1)}.x")
    return bad


def check_tikz() -> list[str]:
    """Для каждого блока ```tikz есть готовый SVG в кэше .tikz/."""
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import tikz
    except ImportError:
        return ["не найден tools/tikz.py"]
    bad = []
    for path, lineno, _code, digest in tikz.collect_blocks():
        if not tikz.cache_path(digest).exists():
            bad.append(f"{path.relative_to(ROOT)}:{lineno}: "
                       f"нет .tikz/{digest}.svg - запустите `make tikz`")
    return bad


def check_headings() -> list[str]:
    """У каждого файла есть заголовок первого уровня.

    Несколько H1 в одном файле допустимы (экзамен, большие справочники
    разбиты на части), поэтому проверка предупреждающая - MkDocs берёт
    заголовок страницы из первого H1.
    """
    bad = []
    for p in iter_markdown(ROOT):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        h1 = [i for i, l in enumerate(lines) if l.startswith("# ")]
        rel = p.relative_to(ROOT)
        if not h1:
            bad.append(f"{rel}: нет заголовка первого уровня")
        elif h1[0] != 0 and any(l.strip() for l in lines[: h1[0]]
                                if not l.startswith(("!", "[", ">"))):
            bad.append(f"{rel}: текст до первого заголовка (строка {h1[0] + 1})")
    return bad


# --------------------------------------------------------------------------
# Проверки собранного сайта
# --------------------------------------------------------------------------

class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.assets: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img" and a.get("src"):
            self.assets.append(a["src"])
        elif tag == "link" and a.get("href") and "stylesheet" in (a.get("rel") or ""):
            self.assets.append(a["href"])
        elif tag == "script" and a.get("src"):
            self.assets.append(a["src"])


def check_built_pages(nav_paths: list[str]) -> list[str]:
    """Каждая страница из nav отрендерена и не пуста."""
    bad = []
    for rel in nav_paths:
        stem = rel[:-3]  # без .md
        candidates = [SITE / f"{stem}.html", SITE / stem / "index.html"]
        if stem == "index":
            candidates.append(SITE / "index.html")
        # README.md и index.md - индексные страницы своего каталога
        if Path(stem).name in ("README", "index"):
            parent = Path(stem).parent
            candidates.append(SITE / parent / "index.html")
        page = next((c for c in candidates if c.exists()), None)
        if page is None:
            bad.append(f"{rel}: страница не собрана")
        elif page.stat().st_size < 1500:
            bad.append(f"{rel}: подозрительно маленькая страница "
                       f"({page.stat().st_size} байт)")
    return bad


def check_built_links() -> tuple[list[str], list[str]]:
    """Внутренние ссылки и ресурсы в собранном HTML ведут на существующие файлы."""
    broken_links, broken_assets = [], []
    base = site_base()
    for page in SITE.rglob("*.html"):
        parser = LinkCollector()
        try:
            parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:  # noqa: BLE001
            broken_links.append(f"{page.relative_to(SITE)}: не разобран ({e})")
            continue

        for group, store in ((parser.links, broken_links),
                             (parser.assets, broken_assets)):
            for href in group:
                if href.startswith(EXTERNAL) or href.startswith("//"):
                    continue
                clean = href.split("#")[0].split("?")[0]
                if not clean:
                    continue
                if clean.startswith("/"):
                    if base and clean.startswith(base + "/"):
                        clean = clean[len(base) + 1:]
                    elif base and clean.rstrip("/") == base:
                        clean = ""
                    root = SITE
                else:
                    root = page.parent
                if not clean:
                    clean = "."
                target = (root / urllib.parse.unquote(clean.lstrip("/"))).resolve()
                if target.is_dir():
                    target = target / "index.html"
                if not target.exists():
                    store.append(f"{page.relative_to(SITE)} -> {href}")
    return broken_links, broken_assets


def check_anchors() -> list[str]:
    """Ссылки вида #раздел ведут на существующий заголовок.

    MkDocs сообщает о таких промахах только на уровне INFO, поэтому
    опечатка в якоре молча доезжает до сайта. Проверяем по готовому HTML:
    там уже учтены и slugify, и заголовки, добавленные темой.
    """
    bad = []
    for page in SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        for anchor in re.findall(r'href="(#[^"]+)"', html):
            anchor = anchor[1:]
            if anchor and anchor not in ids:
                bad.append(f"{page.relative_to(SITE)} -> #{anchor}")
    return bad


def check_site_sanity() -> list[str]:
    """Базовая вменяемость собранного сайта."""
    bad = []
    if not (SITE / "index.html").exists():
        bad.append("нет site/index.html")
    if not (SITE / "search" / "search_index.json").exists():
        bad.append("не собран индекс поиска")
    pages = list(SITE.rglob("*.html"))
    if len(pages) < 40:
        bad.append(f"собрано всего {len(pages)} страниц - ожидалось больше 40")
    css = list((SITE / "assets").rglob("*.css")) if (SITE / "assets").is_dir() else []
    if not css:
        bad.append("не найдены стили темы в site/assets")
    if not (SITE / "stylesheets" / "extra.css").exists():
        bad.append("не скопирован stylesheets/extra.css")
    return bad


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources-only", action="store_true",
                    help="только проверки исходников, без собранного сайта")
    ap.add_argument("--strict-orphans", action="store_true",
                    help="считать материалы вне nav ошибкой, а не предупреждением")
    args = ap.parse_args()

    rep = Report()
    nav_paths, nav_errors = load_nav()

    print("Проверка исходных материалов")
    rep.section("символы (ASCII + кириллица)", check_charset())
    rep.section("ссылки в markdown", check_source_links())
    rep.section("заголовки первого уровня", check_headings(), warn_only=True)
    rep.section("нумерация занятий", check_lesson_numbering())
    rep.section("схемы TikZ отрисованы", check_tikz())

    missing, orphans = check_nav(nav_paths)
    rep.section("mkdocs.yml: разбор nav", nav_errors)
    rep.section("nav: пункты указывают на существующие файлы", missing)
    rep.section("nav: материалы не потеряны", orphans,
                warn_only=not args.strict_orphans)
    print(f"  Всего страниц в nav: {len(nav_paths)}")

    if not args.sources_only:
        print("\nПроверка собранного сайта")
        if not SITE.is_dir():
            print("  [ОШИБКА] каталог site/ не найден - сначала выполните `make build`")
            rep.error("site/ не собран")
        else:
            rep.section("базовая вменяемость", check_site_sanity())
            rep.section("страницы из nav отрендерены", check_built_pages(nav_paths))
            bl, ba = check_built_links()
            rep.section("внутренние ссылки в HTML", bl)
            rep.section("картинки, стили и скрипты", ba)
            rep.section("якоря внутри страниц", check_anchors())
            print(f"  Всего HTML-страниц: {len(list(SITE.rglob('*.html')))}")

    print()
    if rep.warnings:
        print(f"Предупреждений: {len(rep.warnings)}")
    if rep.errors:
        print(f"ОШИБОК: {len(rep.errors)}. Публиковать нельзя.")
        return 1
    print("Все проверки пройдены. Сайт готов к публикации.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
