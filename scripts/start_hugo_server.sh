#!/bin/bash

# Скрипт для автоматического запуска Hugo сервера
set -euo pipefail

echo "🚀 Автоматический запуск Hugo сервера"
echo "====================================="

# Проверяем наличие Hugo
if ! command -v hugo &> /dev/null; then
    echo "❌ Hugo не установлен. Устанавливаем..."
    
    # Определяем ОС
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt update
            sudo apt install -y hugo
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum install -y hugo
        elif command -v dnf &> /dev/null; then
            # Fedora
            sudo dnf install -y hugo
        else
            echo "❌ Не удалось установить Hugo. Установите вручную: https://gohugo.io/installation/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hugo
        else
            echo "❌ Homebrew не установлен. Установите Hugo вручную: https://gohugo.io/installation/"
            exit 1
        fi
    else
        echo "❌ Неподдерживаемая ОС. Установите Hugo вручную: https://gohugo.io/installation/"
        exit 1
    fi
else
    echo "✅ Hugo уже установлен"
fi

# Проверяем версию Hugo
HUGO_VERSION=$(hugo version | head -n1)
echo "📋 Версия Hugo: $HUGO_VERSION"

# Определяем директорию Hugo сайта
HUGO_SITE_DIR=""

# Проверяем аргументы командной строки
if [ $# -eq 1 ]; then
    HUGO_SITE_DIR="$1"
else
    # Ищем hugo.toml в текущей директории и поддиректориях
    if [ -f "hugo.toml" ]; then
        HUGO_SITE_DIR="."
    elif [ -f "config.toml" ]; then
        HUGO_SITE_DIR="."
    elif [ -f "config.yaml" ]; then
        HUGO_SITE_DIR="."
    else
        # Ищем в поддиректориях
        HUGO_SITE_DIR=$(find . -maxdepth 3 -name "hugo.toml" -o -name "config.toml" -o -name "config.yaml" | head -n1 | xargs dirname 2>/dev/null || echo "")
    fi
fi

if [ -z "$HUGO_SITE_DIR" ] || [ ! -d "$HUGO_SITE_DIR" ]; then
    echo "❌ Не найден Hugo сайт. Создаем новый..."
    
    # Создаем новый Hugo сайт
    HUGO_SITE_DIR="./hugo-site"
    hugo new site "$HUGO_SITE_DIR" --force
    
    # Копируем конфигурацию если есть
    if [ -f "configs/hugo.toml" ]; then
        cp configs/hugo.toml "$HUGO_SITE_DIR/"
        echo "✅ Скопирована конфигурация Hugo"
    fi
    
    # Устанавливаем тему PaperMod
    cd "$HUGO_SITE_DIR"
    git init
    git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod
    cd ..
    
    echo "✅ Создан новый Hugo сайт в $HUGO_SITE_DIR"
else
    echo "✅ Найден Hugo сайт в $HUGO_SITE_DIR"
fi

# Переходим в директорию Hugo сайта
cd "$HUGO_SITE_DIR"

# Проверяем наличие темы
if [ ! -d "themes/hugo-papermod" ]; then
    echo "📦 Устанавливаем тему PaperMod..."
    git init
    git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod
fi

# Проверяем наличие контента
if [ ! -d "content" ] || [ -z "$(ls -A content 2>/dev/null)" ]; then
    echo "📝 Создаем пример контента..."
    mkdir -p content/posts
    
    cat > content/posts/hello-world.md << 'EOF'
---
title: "Hello World"
date: 2024-01-15
draft: false
---

# Hello World

Добро пожаловать в ваш новый Hugo сайт!

Это пример страницы, созданной автоматически.

## Возможности

- ✅ Быстрый и легкий
- ✅ Современный дизайн
- ✅ Поддержка Markdown
- ✅ Автоматическое обновление

> [!note] Совет
> Отредактируйте этот файл для изменения содержимого.
EOF
fi

# Настройки сервера
PORT=${PORT:-1313}
BIND=${BIND:-"0.0.0.0"}
BASE_URL="http://localhost:$PORT/"

echo ""
echo "🔧 Настройки сервера:"
echo "   Порт: $PORT"
echo "   Привязка: $BIND"
echo "   URL: $BASE_URL"
echo ""

# Запускаем Hugo сервер
echo "🚀 Запускаем Hugo сервер..."
echo "=================================="
echo ""
echo "📋 Инструкции:"
echo "1. Откройте браузер: $BASE_URL"
echo "2. Для остановки сервера нажмите Ctrl+C"
echo "3. Сервер автоматически перезагружается при изменениях"
echo ""

# Запускаем сервер с подробным выводом
hugo server \
    --port "$PORT" \
    --bind "$BIND" \
    --baseURL "$BASE_URL" \
    --disableFastRender \
    --verbose \
    --log \
    --verboseLog