# Obsidian to Hugo Converter - Описание проекта

## 🎯 Цель проекта

Создать автоматический конвертер для преобразования хранилища Obsidian в Hugo wiki с темой PaperMod, который позволит пользователям легко публиковать свои заметки в виде красивого веб-сайта.

## 🏗 Архитектура проекта

### Модульная структура

```
src/obsidian_to_hugo/
├── core/                    # Основные модели данных
│   ├── __init__.py
│   └── models.py           # Pydantic модели
├── converters/             # Конвертеры
│   ├── __init__.py
│   └── hugo_converter.py   # Основной конвертер
├── watchers/               # Файловые наблюдатели
│   ├── __init__.py
│   └── file_watcher.py     # Наблюдение за изменениями
├── utils/                  # Утилиты
│   ├── __init__.py
│   └── obsidian_parser.py  # Парсер Obsidian
├── cli.py                  # CLI интерфейс
├── main.py                 # Точка входа
└── __main__.py            # Запуск как модуль
```

### Основные компоненты

#### 1. Core Models (`core/models.py`)
- **ObsidianNote**: Модель для представления Obsidian заметки
- **HugoPost**: Модель для представления Hugo поста
- **ConversionConfig**: Конфигурация конвертации
- **ConversionStats**: Статистика процесса конвертации

#### 2. Obsidian Parser (`utils/obsidian_parser.py`)
- Парсинг Obsidian markdown файлов
- Извлечение front matter
- Обработка wikilinks
- Конвертация callouts
- Извлечение тегов

#### 3. Hugo Converter (`converters/hugo_converter.py`)
- Основная логика конвертации
- Создание Hugo front matter
- Копирование вложений
- Построение карты ссылок

#### 4. File Watcher (`watchers/file_watcher.py`)
- Наблюдение за изменениями в Obsidian vault
- Автоматическая переконвертация
- Debouncing для предотвращения частых обновлений

#### 5. CLI Interface (`cli.py`)
- Команда `convert`: Основное преобразование
- Команда `watch`: Режим наблюдения
- Команда `analyze`: Анализ хранилища

## 🔄 Процесс конвертации

### 1. Анализ хранилища
```python
# Поиск всех markdown файлов
obsidian_files = find_markdown_files(vault_path)

# Фильтрация по паттернам
filtered_files = apply_patterns(files, include_patterns, exclude_patterns)
```

### 2. Парсинг файлов
```python
# Для каждого файла
for file_path in obsidian_files:
    # Парсинг front matter и контента
    note = parser.parse_file(file_path)
    
    # Извлечение метаданных
    title = note.title
    tags = note.tags
    links = note.links
```

### 3. Конвертация контента
```python
# Конвертация wikilinks
content = parser.convert_wikilinks(content, link_mapping)

# Конвертация callouts
content = parser.convert_callouts(content)

# Обработка тегов
content = converter.process_tags(content, tags)
```

### 4. Создание Hugo файлов
```python
# Создание front matter
front_matter = converter.create_hugo_front_matter(note)

# Определение пути Hugo
hugo_path = converter.convert_to_hugo_path(relative_path)

# Запись файла
converter.write_hugo_file(hugo_post)
```

### 5. Копирование вложений
```python
# Поиск вложений
attachments = find_attachments(vault_path, extensions)

# Копирование в static директорию
for attachment in attachments:
    copy_to_static(attachment, hugo_static_path)
```

## 🛠 Технологический стек

### Основные зависимости
- **Python 3.12+**: Основной язык
- **Pydantic**: Валидация данных и модели
- **Click**: CLI интерфейс
- **Rich**: Красивый вывод в терминале
- **Watchdog**: Файловое наблюдение
- **Frontmatter**: Парсинг YAML front matter

### Дополнительные инструменты
- **Ruff**: Линтинг и форматирование
- **MyPy**: Проверка типов
- **Pytest**: Тестирование
- **Coverage**: Покрытие тестами

## 📊 Обработка данных

### Входные данные
- Obsidian markdown файлы
- Front matter в YAML формате
- Wikilinks `[[filename]]`
- Callouts `> [!type]`
- Теги `#tag`
- Вложения (изображения, PDF, и др.)

### Выходные данные
- Hugo markdown файлы
- Hugo front matter
- Обычные markdown ссылки
- Hugo admonitions
- Скопированные вложения

### Преобразования

#### Wikilinks
```
Input:  [[filename]]
Output: [filename](/filename/)

Input:  [[filename|Display Text]]
Output: [Display Text](/filename/)
```

#### Callouts
```
Input:  > [!note] Title
        > Content
Output: {{< admonition type="note" title="Title" >}}
        Content
        {{< /admonition >}}
```

#### Front Matter
```
Input:  ---
        title: "My Note"
        tags: [tag1, tag2]
        ---
Output: ---
        title: "My Note"
        tags: [tag1, tag2]
        date: '2024-01-01'
        showToc: true
        ---
```

## 🔧 Конфигурация

### Параметры конвертации
- **Паттерны включения/исключения**: Контроль файлов
- **Расширения вложений**: Типы файлов для копирования
- **Настройки оглавления**: Глубина и включение
- **Обработка тегов**: Извлечение и конвертация
- **Сохранение front matter**: Сохранение оригинальных полей

### Hugo конфигурация
- **Тема PaperMod**: Готовая конфигурация
- **Настройки поиска**: Fuse.js интеграция
- **Меню и навигация**: Автоматическая генерация
- **SEO настройки**: Метаданные и структура

## 🧪 Тестирование

### Unit тесты
- Парсинг Obsidian файлов
- Конвертация wikilinks
- Обработка front matter
- Создание Hugo файлов

### Интеграционные тесты
- Полный процесс конвертации
- Обработка ошибок
- Файловое наблюдение

### Демонстрационные тесты
- Создание тестового хранилища
- Проверка результатов конвертации
- Валидация выходных файлов

## 🚀 Развертывание

### Поддерживаемые платформы
- **GitHub Pages**: Автоматическое развертывание
- **Netlify**: Простая интеграция
- **Vercel**: Быстрое развертывание
- **Любой хостинг**: Статические файлы

### CI/CD
- **GitHub Actions**: Автоматическая сборка
- **Тестирование**: Проверка качества кода
- **Документация**: Автоматическое обновление

## 📈 Метрики и мониторинг

### Статистика конвертации
- Количество обработанных файлов
- Время выполнения
- Количество ошибок
- Статистика вложений

### Качество кода
- Покрытие тестами
- Соответствие стандартам
- Производительность
- Безопасность

## 🔮 Планы развития

### Версия 0.2.0
- Поддержка Dataview запросов
- Конвертация Canvas файлов
- Расширенные настройки темы
- API для интеграции

### Версия 0.3.0
- Веб-интерфейс
- Поддержка других тем
- Экспорт в другие форматы
- Инкрементальная конвертация

## 🤝 Сообщество

### Участие в разработке
- Открытый исходный код
- Приветствуются PR и issues
- Документированные процессы
- Руководство для контрибьюторов

### Поддержка
- Подробная документация
- Примеры использования
- Демонстрационные скрипты
- Активная поддержка сообщества