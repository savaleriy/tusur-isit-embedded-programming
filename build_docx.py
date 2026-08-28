#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from html import escape as html_escape
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("Нужен пакет markdown: pip install markdown (или make install)")

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
import tikz  # noqa: E402

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "style.docx"

TITLE = "Программирование микроконтроллеров"
SUBTITLE = "Конспект курса. ТУСУР, направление 09.03.02"

# Названия занятий для заголовков разделов документа
LESSONS = [
    ("01-safety-electronics", "Техника безопасности и основы электроники"),
    ("02-tooling", "Инструменты разработки и первая программа"),
    ("03-digital-io", "Цифровой ввод-вывод"),
    ("04-pwm", "Широтно-импульсная модуляция"),
    ("05-adc-sensors", "АЦП и аналоговые датчики"),
    ("06-platformio", "PlatformIO"),
    ("07-timing-multitasking", "Время и кооперативная многозадачность"),
    ("08-interrupts", "Прерывания"),
    ("09-timers", "Таймеры и счётчики"),
    ("10-indication", "Индикация: сдвиговые регистры и развёртка"),
    ("11-cpp-oop", "C++ и ООП: собственная библиотека"),
    ("12-i2c-lcd-rtc", "Шина I2C: дисплей, RTC, MPU-6050"),
    ("13-spi-tft-rfid", "Шина SPI: TFT, RFID, SD-карта"),
    ("14-sound-ir", "Звук, ИК-управление и микрофон"),
    ("15-actuators", "Приводы и силовая коммутация"),
    ("16-uart-link", "UART и связь двух микроконтроллеров"),
    ("17-memory", "Память микроконтроллера и энергопотребление"),
    ("18-low-level", "Низкий уровень: регистры, чистый C, ассемблер"),
    ("19-freertos-tasks", "FreeRTOS: задачи и планировщик"),
    ("20-freertos-sync", "FreeRTOS: синхронизация и обмен данными"),
    ("21-freertos-isr", "FreeRTOS: прерывания, тайминги и ресурсы"),
]

MODULES = [
    ("Модуль 1. Базовая Arduino и прерывания", 0, 9),
    ("Модуль 2. Продвинутая Arduino: PlatformIO, библиотеки, C++", 9, 18),
    ("Модуль 3. FreeRTOS", 18, 21),
]


def practice_sections() -> list[tuple[str, str, str]]:
    """(заголовок раздела, путь, вид) для всех занятий, с разбивкой по модулям."""
    out = []
    for module_title, start, end in MODULES:
        out.append((module_title, "", "module"))
        for idx in range(start, end):
            slug, name = LESSONS[idx]
            n = idx + 1
            out.append((f"Занятие {n}. {name}",
                        f"Practice/{slug}/note.md", "chapter"))
            out.append((f"Занятие {n}. {name}. Задачи",
                        f"Practice/{slug}/task.md", "chapter"))
    return out


PARTS: dict[str, list[tuple[str, str, str]]] = {
    "intro": [
        ("О курсе", "README.md", "chapter"),
    ],
    "hardware": [
        ("Аппаратное обеспечение курса", "Hardware/README.md", "chapter"),
    ],
    "practice": practice_sections(),
    "labs": [
        ("Лабораторные работы", "", "module"),
        ("Правила выполнения лабораторных работ", "Labs/README.md", "chapter"),
        ("Лабораторная работа 1. Интерактивное устройство",
         "Labs/lab1-snake/lab.md", "chapter"),
        ("Лабораторная работа 2. Библиотека для датчика",
         "Labs/lab2-sensor-library/lab.md", "chapter"),
        ("Лабораторная работа 3. Система сбора данных",
         "Labs/lab3-greenhouse/lab.md", "chapter"),
        ("Лабораторная работа 4. Многозадачная система на FreeRTOS",
         "Labs/lab4-freertos/lab.md", "chapter"),
    ],
    "appendix": [
        ("Приложения", "", "module"),
        ("Приложение. Язык C", "Appendix/c.md", "chapter"),
        ("Приложение. Язык C++", "Appendix/cpp.md", "chapter"),
        ("Приложение. Среды разработки и симуляторы",
         "Appendix/tooling.md", "chapter"),
        ("Приложение. Датчики Wokwi", "Appendix/wokwi-sensors.md", "chapter"),
    ],
    "exam": [
        ("Вопросы к экзамену", "Exam/exam_2027.md", "chapter"),
    ],
}

ORDER = ["intro", "hardware", "practice", "labs", "appendix", "exam"]


def make_converter() -> "markdown.Markdown":
    return markdown.Markdown(extensions=[
        "fenced_code",
        "tables",
        "toc",
        "sane_lists",
        "attr_list",
        "md_in_html",
    ])


IMG_SRC = re.compile(r'src="(?!https?://|data:)([^"]+)"')


def fix_images(html: str, section_dir: Path) -> str:
    """Делает пути к картинкам абсолютными, чтобы pandoc их нашёл."""
    def repl(m):
        rel = m.group(1)
        path = (section_dir / rel).resolve()
        return f'src="{path}"' if path.exists() else m.group(0)
    return IMG_SRC.sub(repl, html)


def substitute_tikz(md_text: str, missing: list[str], where: str) -> str:
    """Заменяет блоки ```tikz на ссылку к PNG из кэша."""
    def repl(m):
        digest = tikz.block_hash(m.group("code"))
        png = tikz.cache_path_png(digest)
        caption = (m.group("opts") or "").strip()
        if not png.exists():
            missing.append(f"{where}: .tikz/{digest}.png")
            return f"*[схема не отрисована: {digest}]*"
        alt = html_escape(caption) if caption else "схема"
        line = f"![{alt}]({png})"
        return f"{line}\n\n*{caption}*" if caption else line
    return tikz.FENCE.sub(repl, md_text)


def strip_site_only(md_text: str) -> str:
    """Убирает то, что осмысленно только на сайте."""
    # бейджи shields.io и служебные блоки навигации
    md_text = re.sub(r"^!\[[^\]]*\]\(https://img\.shields\.io[^)]*\)\s*$", "",
                     md_text, flags=re.M)
    return md_text


def build(parts: list[str], output: Path) -> int:
    missing_png: list[str] = []
    chunks: list[str] = []
    md = make_converter()
    used = skipped = 0

    for part in parts:
        for title, relpath, kind in PARTS[part]:
            if kind == "module":
                chunks.append(
                    f'<section class="module">\n'
                    f"<h1>{html_escape(title)}</h1>\n</section>\n"
                )
                print(f"  == {title}")
                continue

            path = ROOT / relpath
            if not path.exists():
                print(f"  [пропущен] {relpath}", file=sys.stderr)
                skipped += 1
                continue

            text = path.read_text(encoding="utf-8")
            text = strip_site_only(text)
            text = substitute_tikz(text, missing_png, relpath)
            # первый заголовок файла заменяем на наш - иначе он дублируется
            text = re.sub(r"\A\s*#\s+[^\n]*\n", "", text)

            md.reset()
            body = fix_images(md.convert(text), path.parent)
            chunks.append(
                f'<section class="chapter">\n'
                f"<h1>{html_escape(title)}</h1>\n{body}\n</section>\n"
            )
            print(f"  +  {title}")
            used += 1

    if missing_png:
        print(f"\nНе найдено {len(missing_png)} растровых схем:", file=sys.stderr)
        for m in missing_png[:10]:
            print(f"  {m}", file=sys.stderr)
        print("Выполните: make tikz-png", file=sys.stderr)

    html_doc = (
        '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html_escape(TITLE)}</title>\n</head>\n<body>\n"
        + "\n".join(chunks)
        + "\n</body>\n</html>\n"
    )

    html_path = ROOT / ".docx-build.html"
    html_path.write_text(html_doc, encoding="utf-8")
    size_kb = html_path.stat().st_size // 1024
    print(f"\nHTML собран: {used} разделов, {size_kb} КБ")

    cmd = [
        "pandoc", str(html_path),
        "-o", str(output),
        "--from", "html",
        "--to", "docx",
        "--toc", "--toc-depth=2",
        "--metadata", f"title={TITLE}",
        "--metadata", f"subtitle={SUBTITLE}",
        "--metadata", "lang=ru-RU",
        "--resource-path", str(ROOT),
    ]
    if TEMPLATE.exists():
        cmd += ["--reference-doc", str(TEMPLATE)]

    print("Конвертация в DOCX...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    html_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        print(proc.stderr[-2000:], file=sys.stderr)
        return 1

    print(f"Готово: {output.name} "
          f"({output.stat().st_size // 1024} КБ, пропущено {skipped})")
    return 1 if missing_png else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", action="append", choices=ORDER,
                    help="собрать только указанные части (можно повторять)")
    ap.add_argument("-o", "--output", type=Path,
                    default=ROOT / "Программирование_микроконтроллеров.docx")
    a = ap.parse_args()
    sys.exit(build(a.part or ORDER, a.output))
