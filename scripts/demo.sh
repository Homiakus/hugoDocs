#!/bin/bash

# Демонстрационный скрипт для Obsidian to Hugo converter
set -euo pipefail

echo "🚀 Демонстрация Obsidian to Hugo Converter"
echo "=========================================="

# Создаем временную директорию для демо
DEMO_DIR=$(mktemp -d)
echo "📁 Создана временная директория: $DEMO_DIR"

# Создаем структуру демо Obsidian vault
OBSIDIAN_VAULT="$DEMO_DIR/obsidian_vault"
HUGO_SITE="$DEMO_DIR/hugo_site"

mkdir -p "$OBSIDIAN_VAULT"
mkdir -p "$HUGO_SITE"

echo "📝 Создаем демо Obsidian заметки..."

# Создаем главную заметку
cat > "$OBSIDIAN_VAULT/README.md" << 'EOF'
---
title: "Моя Wiki"
tags: [wiki, главная]
created: 2024-01-01
---

# Добро пожаловать в мою Wiki

Это демонстрационная wiki, созданная из Obsidian хранилища.

## Быстрые ссылки

- [[Программирование]]
- [[Заметки]]
- [[Проекты]]

> [!note] Важно
> Эта wiki автоматически конвертирована из Obsidian с помощью нашего конвертера!

## Теги

#wiki #демо #obsidian
EOF

# Создаем заметку о программировании
cat > "$OBSIDIAN_VAULT/Программирование.md" << 'EOF'
---
title: "Программирование"
tags: [программирование, python, hugo]
created: 2024-01-01
---

# Программирование

Здесь собраны заметки о программировании.

## Python

Python - отличный язык программирования для начинающих.

```python
def hello_world():
    print("Hello, World!")
    return "Hello from Python!"
```

## Hugo

Hugo - быстрый статический генератор сайтов.

> [!tip] Совет
> Hugo отлично подходит для создания блогов и документации.

## Связанные заметки

- [[Заметки]]
- [[Проекты]]
EOF

# Создаем заметку с заметками
cat > "$OBSIDIAN_VAULT/Заметки.md" << 'EOF'
---
title: "Заметки"
tags: [заметки, идеи]
created: 2024-01-01
---

# Заметки

Различные заметки и идеи.

## Идеи проектов

1. Создать конвертер Obsidian → Hugo
2. Написать документацию
3. Создать демо

> [!warning] Внимание
> Некоторые идеи могут быть нереалистичными!

## Ссылки

- [[Программирование]]
- [[Проекты]]
EOF

# Создаем заметку о проектах
cat > "$OBSIDIAN_VAULT/Проекты.md" << 'EOF'
---
title: "Проекты"
tags: [проекты, разработка]
created: 2024-01-01
---

# Проекты

Мои текущие проекты.

## Obsidian to Hugo Converter

Автоматический конвертер для преобразования Obsidian в Hugo.

### Возможности

- ✅ Конвертация wikilinks
- ✅ Обработка тегов
- ✅ Копирование вложений
- ✅ Поддержка callouts

> [!success] Готово
> Проект успешно завершен!

## Связанные заметки

- [[Программирование]]
- [[Заметки]]
EOF

# Создаем подпапку с заметками
mkdir -p "$OBSIDIAN_VAULT/подпапка"
cat > "$OBSIDIAN_VAULT/подпапка/Вложенная заметка.md" << 'EOF'
---
title: "Вложенная заметка"
tags: [вложенная, пример]
---

# Вложенная заметка

Это заметка в подпапке.

## Ссылки на родительские заметки

- [[README]]
- [[Программирование]]

> [!info] Информация
> Эта заметка демонстрирует работу с вложенными папками.
EOF

# Создаем демо изображение
echo "Создаем демо изображение..." > "$OBSIDIAN_VAULT/demo.png"

echo "✅ Демо Obsidian vault создан!"
echo "📊 Статистика:"
echo "   - Файлов: $(find "$OBSIDIAN_VAULT" -name "*.md" | wc -l)"
echo "   - Папок: $(find "$OBSIDIAN_VAULT" -type d | wc -l)"
echo "   - Вложений: $(find "$OBSIDIAN_VAULT" -name "*.png" | wc -l)"

# Переходим в Hugo директорию
cd "$HUGO_SITE"

echo ""
echo "🔧 Настраиваем Hugo сайт..."

# Копируем конфигурацию Hugo
cp /workspace/configs/hugo.toml .

# Создаем структуру Hugo
mkdir -p content static archetypes

echo "🔄 Запускаем конвертацию..."

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
        head -20 "$file"
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
echo "4. Очистите временные файлы:"
echo "   rm -rf $DEMO_DIR"
echo ""
echo "🎉 Демонстрация завершена!"