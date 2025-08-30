#!/bin/bash

# Демонстрационный скрипт для тестирования поддержки GLTF и PDF файлов
set -euo pipefail

echo "🚀 Демонстрация поддержки GLTF и PDF файлов"
echo "=========================================="

# Создаем временную директорию для демо
DEMO_DIR=$(mktemp -d)
echo "📁 Создана временная директория: $DEMO_DIR"

# Создаем структуру демо Obsidian vault
OBSIDIAN_VAULT="$DEMO_DIR/obsidian_vault"
HUGO_SITE="$DEMO_DIR/hugo_site"

mkdir -p "$OBSIDIAN_VAULT"
mkdir -p "$HUGO_SITE"

echo "📝 Создаем демо Obsidian заметки с медиа файлами..."

# Создаем заметку с GLTF моделью
cat > "$OBSIDIAN_VAULT/3D-Models.md" << 'EOF'
---
title: "3D Models Collection"
tags: [3d, models, gltf]
created: 2024-01-01
---

# 3D Models Collection

Здесь собраны 3D модели в формате GLTF.

## Robot Model

[Robot Model](robot.gltf)

## Car Model

[Car Model](car.glb)

## House Model

[House Model](house.gltf)

> [!note] Информация
> Все модели можно просматривать интерактивно в браузере!
EOF

# Создаем заметку с PDF документами
cat > "$OBSIDIAN_VAULT/Documents.md" << 'EOF'
---
title: "Documents Collection"
tags: [documents, pdf]
created: 2024-01-01
---

# Documents Collection

Здесь собраны PDF документы.

## User Manual

[User Manual](manual.pdf)

## Technical Specification

[Technical Specification](spec.pdf)

## Project Report

[Project Report](report.pdf)

> [!info] Просмотр
> Все PDF файлы можно просматривать прямо в браузере!
EOF

# Создаем заметку с изображениями
cat > "$OBSIDIAN_VAULT/Images.md" << 'EOF'
---
title: "Images Collection"
tags: [images, photos]
created: 2024-01-01
---

# Images Collection

Здесь собраны изображения.

## Screenshot

![Screenshot](screenshot.png)

## Diagram

![Diagram](diagram.svg)

## Photo

![Photo](photo.jpg)

> [!tip] Совет
> Кликните на изображение для увеличения!
EOF

# Создаем демо файлы
echo "Creating demo GLTF file..." > "$OBSIDIAN_VAULT/robot.gltf"
echo "Creating demo GLB file..." > "$OBSIDIAN_VAULT/car.glb"
echo "Creating demo house GLTF file..." > "$OBSIDIAN_VAULT/house.gltf"
echo "Creating demo PDF file..." > "$OBSIDIAN_VAULT/manual.pdf"
echo "Creating demo PDF file..." > "$OBSIDIAN_VAULT/spec.pdf"
echo "Creating demo PDF file..." > "$OBSIDIAN_VAULT/report.pdf"
echo "Creating demo image file..." > "$OBSIDIAN_VAULT/screenshot.png"
echo "Creating demo SVG file..." > "$OBSIDIAN_VAULT/diagram.svg"
echo "Creating demo image file..." > "$OBSIDIAN_VAULT/photo.jpg"

echo "✅ Демо Obsidian vault с медиа файлами создан!"
echo "📊 Статистика:"
echo "   - Markdown файлов: $(find "$OBSIDIAN_VAULT" -name "*.md" | wc -l)"
echo "   - GLTF/GLB файлов: $(find "$OBSIDIAN_VAULT" -name "*.gltf" -o -name "*.glb" | wc -l)"
echo "   - PDF файлов: $(find "$OBSIDIAN_VAULT" -name "*.pdf" | wc -l)"
echo "   - Image файлов: $(find "$OBSIDIAN_VAULT" -name "*.png" -o -name "*.jpg" -o -name "*.svg" | wc -l)"

# Переходим в Hugo директорию
cd "$HUGO_SITE"

echo ""
echo "🔧 Настраиваем Hugo сайт..."

# Копируем конфигурацию Hugo
cp /workspace/configs/hugo.toml .

# Создаем структуру Hugo
mkdir -p content static archetypes layouts/shortcodes

# Копируем shortcodes
cp /workspace/layouts/shortcodes/* layouts/shortcodes/ 2>/dev/null || true

echo "🔄 Запускаем конвертацию с поддержкой медиа файлов..."

# Запускаем конвертер
python3 -m obsidian_to_hugo convert \
  --obsidian-vault "$OBSIDIAN_VAULT" \
  --hugo-content ./content \
  --hugo-static ./static \
  --hugo-archetypes ./archetypes \
  --theme "hugo-papermod" \
  --toc-max-depth 3

echo ""
echo "✅ Конвертация завершена!"
echo "📊 Результат:"
echo "   - Hugo файлов: $(find ./content -name "*.md" | wc -l)"
echo "   - Вложений скопировано: $(find ./static -type f | wc -l)"

echo ""
echo "📖 Содержимое конвертированных файлов:"
echo "======================================"

# Показываем содержимое конвертированных файлов
for file in ./content/*.md; do
    if [ -f "$file" ]; then
        echo ""
        echo "📄 $(basename "$file"):"
        echo "---"
        head -30 "$file"
        echo "..."
    fi
done

echo ""
echo "🎯 Следующие шаги:"
echo "1. Установите тему PaperMod:"
echo "   git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod"
echo ""
echo "2. Запустите Hugo сервер:"
echo "   cd $HUGO_SITE"
echo "   hugo server -D"
echo ""
echo "3. Откройте браузер: http://localhost:1313"
echo ""
echo "4. Проверьте:"
echo "   - 3D модели в заметке '3D Models Collection'"
echo "   - PDF документы в заметке 'Documents Collection'"
echo "   - Изображения в заметке 'Images Collection'"
echo ""
echo "5. Очистите временные файлы:"
echo "   rm -rf $DEMO_DIR"
echo ""
echo "🎉 Демонстрация поддержки медиа файлов завершена!"