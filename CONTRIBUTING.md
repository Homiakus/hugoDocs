# Руководство по участию в разработке

Спасибо за интерес к проекту Obsidian to Hugo Converter! Мы приветствуем вклад от сообщества.

## 🚀 Быстрый старт

1. **Форкните репозиторий**
2. **Клонируйте ваш форк:**
   ```bash
   git clone https://github.com/your-username/obsidian-to-hugo.git
   cd obsidian-to-hugo
   ```

3. **Создайте виртуальное окружение:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # или
   .venv\Scripts\activate     # Windows
   ```

4. **Установите зависимости:**
   ```bash
   pip install -e .[dev]
   ```

5. **Создайте ветку для ваших изменений:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный тест
pytest tests/unit/test_obsidian_parser.py::TestObsidianParser::test_parse_file_with_front_matter
```

### Линтинг и форматирование
```bash
# Проверка кода
ruff check src/

# Автоматическое исправление
ruff check --fix src/

# Форматирование
ruff format src/

# Проверка типов
mypy src/
```

## 📝 Стиль кода

### Python
- Следуйте [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Используйте type hints
- Документируйте функции и классы
- Пишите тесты для нового функционала

### Структура коммитов
Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: maintenance tasks
```

### Примеры

```python
from typing import List, Optional
from pathlib import Path

def convert_file(file_path: Path, config: ConversionConfig) -> Optional[HugoPost]:
    """
    Convert a single Obsidian file to Hugo format.
    
    Args:
        file_path: Path to the Obsidian file
        config: Conversion configuration
        
    Returns:
        HugoPost object or None if conversion fails
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Implementation here
    return hugo_post
```

## 🐛 Сообщение об ошибках

### Создание Issue

1. **Проверьте существующие issues** - возможно, ваша проблема уже известна
2. **Используйте шаблон** - заполните все необходимые поля
3. **Опишите проблему подробно:**
   - Что вы делали?
   - Что произошло?
   - Что ожидали увидеть?
   - Версии Python, Hugo, ОС
   - Логи ошибок

### Пример хорошего issue

```markdown
## Описание
При конвертации файла с кириллическими символами в названии возникает ошибка.

## Шаги для воспроизведения
1. Создайте файл `Тест.md` в Obsidian
2. Запустите конвертер
3. Получите ошибку

## Ожидаемое поведение
Файл должен конвертироваться без ошибок

## Фактическое поведение
```
Error: 'ascii' codec can't encode character '\u0442'
```

## Окружение
- Python: 3.12.0
- OS: Ubuntu 22.04
- Obsidian: 1.5.0
```

## 🔧 Разработка новых функций

### Процесс разработки

1. **Создайте issue** с описанием функции
2. **Обсудите подход** в issue
3. **Создайте ветку** для разработки
4. **Реализуйте функцию** с тестами
5. **Обновите документацию**
6. **Создайте Pull Request**

### Структура Pull Request

```markdown
## Описание
Краткое описание изменений

## Тип изменений
- [ ] Исправление ошибки
- [ ] Новая функция
- [ ] Улучшение документации
- [ ] Рефакторинг

## Тестирование
- [ ] Добавлены unit тесты
- [ ] Протестировано вручную
- [ ] Обновлена документация

## Чеклист
- [ ] Код следует стилю проекта
- [ ] Добавлены тесты для нового функционала
- [ ] Обновлена документация
- [ ] Все тесты проходят
- [ ] Линтер не выдает ошибок
```

## 📚 Документация

### Обновление документации

- Обновляйте README.md при добавлении новых функций
- Добавляйте примеры использования
- Обновляйте CHANGELOG.md
- Проверяйте актуальность EXAMPLE.md

### Документирование кода

```python
class HugoConverter:
    """
    Converts Obsidian notes to Hugo format.
    
    This class handles the main conversion logic, including:
    - Parsing Obsidian files
    - Converting wikilinks
    - Processing front matter
    - Copying attachments
    
    Example:
        >>> config = ConversionConfig(...)
        >>> converter = HugoConverter(config)
        >>> stats = converter.convert()
        >>> print(f"Converted {stats.converted_files} files")
    """
    
    def convert(self) -> ConversionStats:
        """
        Convert all Obsidian files to Hugo format.
        
        Returns:
            ConversionStats: Statistics about the conversion process
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If Obsidian vault doesn't exist
        """
```

## 🎯 Области для улучшения

### Приоритетные задачи
- [ ] Поддержка Dataview запросов
- [ ] Конвертация Canvas файлов
- [ ] Улучшение обработки ошибок
- [ ] Оптимизация производительности
- [ ] Расширенные настройки темы

### Хорошие первые задачи
- [ ] Добавление новых тестов
- [ ] Улучшение документации
- [ ] Исправление мелких ошибок
- [ ] Добавление новых примеров

## 🤝 Коммуникация

### Каналы связи
- **Issues**: Для багов и предложений функций
- **Discussions**: Для общих вопросов и обсуждений
- **Pull Requests**: Для кода

### Правила поведения
- Будьте уважительны к другим участникам
- Используйте конструктивную критику
- Помогайте новым участникам
- Следуйте принципам открытого исходного кода

## 📄 Лицензия

Участвуя в проекте, вы соглашаетесь с тем, что ваш вклад будет лицензирован под MIT License.

## 🙏 Благодарности

Спасибо всем, кто вносит вклад в проект! Каждый PR, issue и комментарий помогает сделать проект лучше.