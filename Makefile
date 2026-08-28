# Сборка, проверка и публикация материалов курса
# "Программирование микроконтроллеров"
#
# Makefile - единственная точка входа: те же цели вызывает GitHub Actions,
# поэтому локальная проверка и проверка в CI дают одинаковый результат.
#
# Быстрый старт:
#   make install    один раз - зависимости в .venv
#   make serve      локальный просмотр на http://127.0.0.1:8000
#   make test       ПОЛНАЯ проверка перед публикацией
#   make deploy     публикация на GitHub Pages
#
# Материалы лежат в Practice/, Labs/, Hardware/, Appendix/, Exam/, Students/.
# Каталог docs/ - генерируемая копия для MkDocs, в репозиторий не попадает.

SHELL := /bin/bash

VENV    := .venv
PY      := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
MKDOCS  := $(VENV)/bin/mkdocs
PORT    ?= 8000
DOCX    ?= Программирование_микроконтроллеров.docx

.DEFAULT_GOAL := help
.PHONY: help install docs build serve check check-sources test links \
        tikz tikz-png tikz-force tikz-clean stats docx deploy \
        clean distclean ci ci-build ci-check

# --------------------------------------------------------------------------

help:
	@echo "Материалы курса - доступные команды:"
	@echo
	@echo "  Разработка"
	@echo "    make install       установить зависимости в $(VENV)"
	@echo "    make serve         локальный сервер на порту $(PORT) с автообновлением"
	@echo "    make build         собрать сайт в site/ (строгий режим)"
	@echo
	@echo "  Проверка"
	@echo "    make test          ПОЛНАЯ проверка: сборка с нуля + все проверки"
	@echo "    make check-sources быстрые проверки исходников без сборки"
	@echo "    make check         проверки по собранному сайту"
	@echo "    make links         проверка внешних ссылок (нужен интернет)"
	@echo
	@echo "  Схемы"
	@echo "    make tikz          отрисовать схемы TikZ в SVG (нужен LaTeX)"
	@echo "    make tikz-png      дополнительно растр для DOCX"
	@echo "    make tikz-force    перерисовать все схемы заново"
	@echo
	@echo "  Публикация"
	@echo "    make docx          собрать конспект в DOCX (нужен pandoc)"
	@echo "    make deploy        опубликовать на GitHub Pages"
	@echo
	@echo "  Прочее"
	@echo "    make stats         объём материалов курса"
	@echo "    make clean         удалить site/ и docs/"
	@echo "    make distclean     удалить также $(VENV)"

# --------------------------------------------------------------------------
# Зависимости
# --------------------------------------------------------------------------

$(VENV)/bin/activate: requirements.txt
	@echo "==> Создание виртуального окружения"
	python3 -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -r requirements.txt
	@touch $(VENV)/bin/activate
	@echo "==> Зависимости установлены"

install: $(VENV)/bin/activate

# --------------------------------------------------------------------------
# Схемы TikZ
# --------------------------------------------------------------------------
# Блоки ```tikz в конспектах компилируются в SVG и кладутся в .tikz/.
# Кэш коммитится, поэтому сборка сайта в CI не требует установленного LaTeX.

tikz: install
	@$(PY) tools/tikz.py

tikz-png: install
	@$(PY) tools/tikz.py --png

tikz-force: install
	@$(PY) tools/tikz.py --force --png --prune

tikz-clean:
	@rm -rf .tikz/

# --------------------------------------------------------------------------
# Сборка сайта
# --------------------------------------------------------------------------

docs: install
	@$(PY) tools/build_docs.py

# --strict превращает предупреждения MkDocs в ошибки:
# битые ссылки внутри markdown, пункты nav без файлов, отсутствующие ресурсы.
build: docs
	@$(PY) tools/tikz.py --check >/dev/null 2>&1 || $(PY) tools/tikz.py
	@echo "==> Сборка сайта (строгий режим)"
	@$(MKDOCS) build --strict --clean
	@echo "==> Готово: site/"

serve: docs
	@echo "==> http://127.0.0.1:$(PORT)  (Ctrl+C для остановки)"
	@$(MKDOCS) serve --dev-addr 127.0.0.1:$(PORT)

# --------------------------------------------------------------------------
# Проверки
# --------------------------------------------------------------------------

# Быстрая проверка исходников: символы, ссылки, заголовки, нумерация, схемы, nav.
# Сборка не требуется - удобно запускать во время правки материалов.
check-sources: install
	@$(PY) tools/check_site.py --sources-only

# Проверка по собранному сайту. Требует, чтобы site/ уже существовал.
check: install
	@$(PY) tools/check_site.py

# Главная команда перед публикацией: собрать с нуля и проверить всё.
test: clean build check
	@echo
	@echo "==> Сайт проверен и готов к публикации."
	@echo "    Просмотреть локально: make serve"
	@echo "    Опубликовать:         make deploy"

# Проверка внешних ссылок вынесена отдельно: требует сети и работает долго.
links: build
	@echo "==> Проверка внешних ссылок"
	@$(PIP) install --quiet linkchecker 2>/dev/null || true
	@if [ -x $(VENV)/bin/linkchecker ]; then \
		$(VENV)/bin/linkchecker --check-extern --ignore-url='^mailto:' \
			--no-warnings site/index.html || true; \
	else \
		echo "    linkchecker не установлен, проверяю только доступность доменов"; \
		grep -rhoE 'https?://[^"<>) ]+' --include='*.md' \
			Practice Labs Hardware Appendix Exam README.md \
			| sed -E 's#(https?://[^/]+).*#\1#' | sort -u \
			| while read -r u; do \
				code=$$(curl -s -o /dev/null -w '%{http_code}' -m 10 -L "$$u" || echo "---"); \
				case "$$code" in 2*|3*) ;; *) echo "    [$$code] $$u";; esac; \
			done; \
	fi

# --------------------------------------------------------------------------
# Цели для GitHub Actions
# --------------------------------------------------------------------------
# Workflow вызывает только эти цели, чтобы локальная проверка и проверка
# в CI выполняли ровно один и тот же набор шагов.

# Быстрый отсев до сборки: не тратим время на MkDocs, если сломаны ссылки.
ci-build: install
	@$(PY) tools/check_site.py --sources-only --strict-orphans
	@$(MAKE) --no-print-directory build

# Полная проверка по собранному сайту (включает и проверки исходников).
ci-check: install
	@$(PY) tools/check_site.py --strict-orphans

ci: ci-build ci-check
	@echo "==> CI: все проверки пройдены"

# --------------------------------------------------------------------------
# Публикация
# --------------------------------------------------------------------------

docx: install tikz-png
	@command -v pandoc >/dev/null || { echo "Нужен pandoc: sudo pacman -S pandoc"; exit 1; }
	@$(PY) build_docx.py -o "$(DOCX)"

deploy: test
	@echo "==> Публикация на GitHub Pages"
	@$(MKDOCS) gh-deploy --force
	@echo "==> Опубликовано: https://savaleriy.github.io/tusur-isit-embedded-programming/"

# --------------------------------------------------------------------------
# Прочее
# --------------------------------------------------------------------------

stats:
	@echo "Объём материалов курса:"
	@printf "  %-12s %6s %8s %10s\n" "раздел" "файлов" "строк" "символов"
	@for d in Practice Labs Hardware Appendix Exam; do \
		f=$$(find $$d -name '*.md' 2>/dev/null | wc -l); \
		l=$$(find $$d -name '*.md' -exec cat {} + 2>/dev/null | wc -l); \
		c=$$(find $$d -name '*.md' -exec cat {} + 2>/dev/null | wc -m); \
		printf "  %-12s %6s %8s %10s\n" "$$d" "$$f" "$$l" "$$c"; \
	done
	@printf "  %-12s %6s %8s %10s\n" "README.md" "1" "$$(wc -l < README.md)" "$$(wc -m < README.md)"
	@echo "  картинок: $$(find Practice Labs Hardware Appendix -type f \( -name '*.png' -o -name '*.jpg' \) 2>/dev/null | wc -l)"
	@echo "  схем TikZ: $$(grep -rho '^```tikz' --include='*.md' Practice Labs Hardware Appendix 2>/dev/null | wc -l)"

clean:
	@rm -rf site/
	@$(PY) tools/build_docs.py --clean 2>/dev/null || rm -rf docs/
	@rm -f .docx-build.html
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

distclean: clean
	@rm -rf $(VENV)
	@echo "Удалено виртуальное окружение"
