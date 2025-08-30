# Obsidian to Hugo Converter

Автоматический конвертер для преобразования хранилища Obsidian в Hugo wiki с темой PaperMod.

## 🚀 Возможности

- ✅ **Автоматическое преобразование** Obsidian заметок в Hugo формат
- ✅ **Поддержка темы PaperMod** с полной настройкой
- ✅ **Конвертация wikilinks** в обычные markdown ссылки
- ✅ **Обработка тегов** из front matter и контента
- ✅ **Копирование вложений** (изображения, PDF, GLTF 3D модели, и др.)
- ✅ **Конвертация callouts** в Hugo admonitions
- ✅ **Автоматическое создание оглавления**
- ✅ **Режим наблюдения** за изменениями в реальном времени
- ✅ **Анализ структуры** хранилища Obsidian
- ✅ **Готовые конфигурации** для развертывания

## 📋 Требования

- Python 3.12+
- Hugo (для просмотра результата)
- Git (для управления темой)

## 🛠 Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd obsidian-to-hugo
```

2. **Установите зависимости:**
```bash
pip install -e .
```

3. **Установите Hugo:**
```bash
# macOS
brew install hugo

# Ubuntu/Debian
sudo apt-get install hugo

# Windows
choco install hugo
```

## 🎯 Быстрый старт

### 1. Настройка Hugo сайта

```bash
# Запустите скрипт настройки
./scripts/setup_hugo.sh

# Установите тему PaperMod
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod
```

### 2. Конвертация хранилища

```bash
# Базовое преобразование
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /path/to/your/obsidian/vault \
  --hugo-content ./content \
  --hugo-static ./static

# С дополнительными опциями
python3 -m obsidian_to_hugo convert \
  --obsidian-vault /path/to/your/obsidian/vault \
  --hugo-content ./content \
  --hugo-static ./static \
  --include-patterns "*.md" "*.markdown" \
  --exclude-patterns "**/draft/*" "**/private/*" \
  --attachment-extensions png jpg pdf mp4 \
  --toc-max-depth 4
```

### 3. Запуск Hugo сервера

```bash
# Режим разработки
hugo server -D

# Сборка для продакшена
hugo
```

## 📖 Использование

### Команды CLI

#### `convert` - Основное преобразование

```bash
python3 -m obsidian_to_hugo convert [OPTIONS]
```

**Опции:**
- `--obsidian-vault, -i` - Путь к хранилищу Obsidian (обязательно)
- `--hugo-content, -c` - Путь к директории content Hugo (по умолчанию: `./content`)
- `--hugo-static, -s` - Путь к директории static Hugo (по умолчанию: `./static`)
- `--hugo-archetypes, -a` - Путь к директории archetypes Hugo (по умолчанию: `./archetypes`)
- `--theme, -t` - Название темы Hugo (по умолчанию: `hugo-papermod`)
- `--include-patterns` - Паттерны файлов для включения (можно указать несколько раз)
- `--exclude-patterns` - Паттерны файлов для исключения (можно указать несколько раз)
- `--attachment-extensions` - Расширения файлов для копирования как вложения
- `--no-wikilinks` - Отключить конвертацию wikilinks
- `--no-tags` - Отключить конвертацию тегов
- `--no-attachments` - Отключить копирование вложений
- `--no-toc` - Отключить создание оглавления
- `--toc-max-depth` - Максимальная глубина оглавления (по умолчанию: 3)
- `--no-front-matter` - Не сохранять оригинальный front matter

#### `watch` - Режим наблюдения

```bash
python3 -m obsidian_to_hugo watch [OPTIONS]
```

Автоматически отслеживает изменения в хранилище Obsidian и переконвертирует файлы.

#### `analyze` - Анализ хранилища

```bash
python3 -m obsidian_to_hugo analyze --obsidian-vault /path/to/vault
```

Показывает статистику хранилища: количество файлов, тегов, ссылок.

### Примеры использования

#### Базовое преобразование

```bash
python3 -m obsidian_to_hugo convert \
  --obsidian-vault ~/Documents/Obsidian/MyVault \
  --hugo-content ./content \
  --hugo-static ./static
```

#### Преобразование с исключениями

```bash
python3 -m obsidian_to_hugo convert \
  --obsidian-vault ~/Documents/Obsidian/MyVault \
  --exclude-patterns "**/draft/*" "**/private/*" "**/temp/*" \
  --include-patterns "*.md" "*.markdown"
```

#### Режим наблюдения

```bash
python3 -m obsidian_to_hugo watch \
  --obsidian-vault ~/Documents/Obsidian/MyVault \
  --hugo-content ./content
```

## 🔧 Конфигурация

### Настройки конвертации

Программа поддерживает множество настроек через параметры командной строки:

- **Паттерны файлов**: Укажите, какие файлы включать/исключать
- **Вложения**: Настройте, какие типы файлов копировать
- **Wikilinks**: Включите/отключите конвертацию внутренних ссылок
- **Теги**: Настройте обработку тегов
- **Оглавление**: Настройте автоматическое создание TOC

### Настройка темы PaperMod

После установки темы вы можете настроить её в `hugo.toml`:

```toml
[params]
  title = "Моя Wiki"
  description = "Конвертировано из Obsidian"
  author = "Ваше имя"
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowShareButtons = true
  ShowPostNavLinks = true
  ShowBreadCrumbs = true
  ShowCodeCopyButtons = true
  ShowWordCount = true
  UseHugoToc = true
```

## 🚀 Развертывание

### GitHub Pages

1. Включите GitHub Pages в настройках репозитория
2. Установите источник на GitHub Actions
3. Используйте готовый workflow в `.github/workflows/hugo.yml`

### Netlify

1. Подключите репозиторий к Netlify
2. Установите команду сборки: `hugo`
3. Установите директорию публикации: `public`

### Vercel

1. Импортируйте репозиторий в Vercel
2. Установите команду сборки: `hugo`
3. Установите выходную директорию: `public`

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov-report=html

# Запуск линтера
ruff check src/

# Проверка типов
mypy src/
```

## 📁 Структура проекта

```
obsidian-to-hugo/
├── src/obsidian_to_hugo/
│   ├── core/           # Основные модели данных
│   ├── converters/     # Конвертеры
│   ├── watchers/       # Файловые наблюдатели
│   ├── utils/          # Утилиты
│   ├── cli.py          # CLI интерфейс
│   └── main.py         # Точка входа
├── tests/              # Тесты
├── configs/            # Конфигурации Hugo
├── scripts/            # Скрипты настройки
├── docs/               # Документация
└── README.md
```

## 🔄 Что конвертируется

### ✅ Поддерживается

- **Markdown файлы** с front matter
- **Wikilinks** `[[filename]]` → `[filename](/filename/)`
- **Теги** из front matter и контента
- **Callouts** → Hugo admonitions
- **Вложения** (изображения, PDF, GLTF 3D модели, и др.)
- **Структура папок**
- **Front matter** (с сохранением оригинальных полей)
- **Интерактивные 3D просмотрщики** для GLTF/GLB файлов
- **Встроенные PDF просмотрщики** с возможностью скачивания

### ⚠️ Ограничения

- **Dataview** запросы не конвертируются
- **Canvas** файлы не поддерживаются
- **Плагины Obsidian** не переносятся
- **Настройки темы** нужно настраивать отдельно

## 🎯 Демонстрация

Запустите демонстрационный скрипт для быстрого тестирования:

```bash
./scripts/demo.sh
```

Этот скрипт создаст тестовое Obsidian хранилище и покажет процесс конвертации.

### Демонстрация медиа файлов

Для тестирования поддержки GLTF и PDF файлов:

```bash
./scripts/demo_media.sh
```

Этот скрипт создаст примеры с 3D моделями и PDF документами.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE).

## 🆘 Поддержка

- **Issues**: Создайте issue в GitHub
- **Discussions**: Используйте Discussions для вопросов
- **Wiki**: Дополнительная документация

## 🙏 Благодарности

- [Hugo](https://gohugo.io/) - Статический генератор сайтов
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) - Тема для Hugo
- [Obsidian](https://obsidian.md/) - Приложение для заметок
