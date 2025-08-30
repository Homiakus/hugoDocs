# Пример использования Obsidian to Hugo Converter

Этот файл демонстрирует, как использовать конвертер для преобразования вашего Obsidian хранилища в Hugo wiki.

## 🎯 Быстрый пример

### 1. Подготовка

Предположим, у вас есть Obsidian хранилище в `/home/user/obsidian-vault`:

```
obsidian-vault/
├── README.md
├── Projects/
│   ├── Project A.md
│   └── Project B.md
├── Notes/
│   ├── Meeting Notes.md
│   └── Ideas.md
└── Attachments/
    ├── diagram.png
    └── document.pdf
```

### 2. Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/obsidian-to-hugo.git
cd obsidian-to-hugo

# Установите зависимости
pip install -e .

# Настройте Hugo
./scripts/setup_hugo.sh
```

### 3. Конвертация

```bash
# Базовое преобразование
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /home/user/obsidian-vault \
  --hugo-content ./content \
  --hugo-static ./static

# Результат:
# ✅ 5 файлов конвертировано
# ✅ 2 вложения скопировано
# ✅ 15 ссылок обработано
# ✅ 8 тегов извлечено
```

### 4. Запуск Hugo

```bash
# Установите тему PaperMod
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod

# Запустите сервер разработки
hugo server -D

# Откройте http://localhost:1313
```

## 📝 Примеры конвертации

### Исходный Obsidian файл

```markdown
---
title: "Мой проект"
tags: [project, python, web]
created: 2024-01-15
---

# Мой проект

Это описание моего проекта.

## Функции

- [[Feature A]]
- [[Feature B]]

> [!note] Важно
> Не забудьте про [[README]]!

## Код

```python
def hello():
    print("Hello, World!")
```

#python #web #project
```

### Результат конвертации в Hugo

```markdown
---
title: "Мой проект"
tags: [project, python, web]
created: 2024-01-15
date: '2024-01-15'
lastmod: '2024-01-15'
showToc: true
TocOpen: false
hideSummary: false
showWordCount: true
showReadingTime: true
---

{{< toc maxdepth="3" >}}

# Мой проект

Это описание моего проекта.

## Функции

- [Feature A](/feature-a/)
- [Feature B](/feature-b/)

{{< admonition type="note" title="Note" >}}
Не забудьте про [README](/readme/)!
{{< /admonition >}}

## Код

```python
def hello():
    print("Hello, World!")
```
```

## 🔧 Продвинутые настройки

### Исключение файлов

```bash
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /home/user/obsidian-vault \
  --exclude-patterns "**/draft/*" "**/private/*" "**/temp/*" \
  --include-patterns "*.md" "*.markdown"
```

### Настройка вложений

```bash
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /home/user/obsidian-vault \
  --attachment-extensions png jpg pdf docx mp4 \
  --no-attachments  # Отключить копирование вложений
```

### Настройка оглавления

```bash
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /home/user/obsidian-vault \
  --toc-max-depth 4 \
  --no-toc  # Отключить оглавление
```

### Режим наблюдения

```bash
# Автоматическая конвертация при изменениях
python3 -m obsidian_to_hugo watch \
  --obsidian-vault /home/user/obsidian-vault \
  --hugo-content ./content
```

## 📊 Анализ хранилища

```bash
python3 -m obsidian_to_hugo analyze \
  --obsidian-vault /home/user/obsidian-vault
```

Результат:
```
               Obsidian Vault Analysis               
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric       ┃ Value                              ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Files  │ 25                                 │
│ Unique Tags  │ 18                                 │
│ Unique Links │ 12                                 │
│ Vault Path   │ /home/user/obsidian-vault         │
└──────────────┴────────────────────────────────────┘

Tags found: project, python, web, meeting, ideas, ...

Links found: Feature A, Feature B, README, ...
```

## 🚀 Развертывание

### GitHub Pages

1. Создайте репозиторий на GitHub
2. Настройте GitHub Actions:

```yaml
# .github/workflows/hugo.yml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
      - name: Build
        run: hugo
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
```

### Netlify

1. Подключите репозиторий к Netlify
2. Настройте:
   - Build command: `hugo`
   - Publish directory: `public`

### Vercel

1. Импортируйте репозиторий в Vercel
2. Настройте:
   - Build command: `hugo`
   - Output directory: `public`

## 🎨 Настройка темы

Отредактируйте `hugo.toml`:

```toml
[params]
  title = "Моя Wiki"
  description = "Персональная wiki, конвертированная из Obsidian"
  author = "Ваше имя"
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowShareButtons = true
  ShowPostNavLinks = true
  ShowBreadCrumbs = true
  ShowCodeCopyButtons = true
  ShowWordCount = true
  UseHugoToc = true

[params.homeInfoParams]
  Title = "Добро пожаловать 👋"
  Content = "Это моя персональная wiki, созданная из Obsidian хранилища"

[params.profileMode]
  enabled = false

[params.socialIcons]
  - name = github
    url = "https://github.com/your-username"
```

## 🔍 Поиск и навигация

После конвертации ваша wiki будет иметь:

- **Автоматическое оглавление** на каждой странице
- **Навигацию по тегам** (`/tags/`)
- **Поиск** (встроенный в тему PaperMod)
- **Хлебные крошки** для навигации
- **Связанные посты** в конце страниц

## 🎯 Демонстрация

Запустите демо для быстрого тестирования:

```bash
./scripts/demo.sh
```

Это создаст тестовое хранилище и покажет весь процесс конвертации.

## 📚 Дополнительные ресурсы

- [Hugo Documentation](https://gohugo.io/documentation/)
- [PaperMod Theme](https://github.com/adityatelange/hugo-PaperMod)
- [Obsidian Documentation](https://help.obsidian.md/)