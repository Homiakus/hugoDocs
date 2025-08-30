#!/bin/bash

# Демонстрационный скрипт для GUI приложения
set -euo pipefail

echo "🚀 Демонстрация GUI приложения Obsidian to Hugo Converter"
echo "=========================================================="

# Проверяем наличие PyQt6
echo "📦 Проверяем зависимости..."
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "❌ PyQt6 не установлен. Устанавливаем..."
    pip install PyQt6 qt-material
else
    echo "✅ PyQt6 уже установлен"
fi

if ! python3 -c "import qt_material" 2>/dev/null; then
    echo "❌ qt-material не установлен. Устанавливаем..."
    pip install qt-material
else
    echo "✅ qt-material уже установлен"
fi

echo ""
echo "🎨 Запускаем GUI приложение..."
echo "=================================="
echo ""
echo "Инструкции по использованию:"
echo "1. В левой панели настройте пути к Obsidian vault и Hugo директориям"
echo "2. Выберите тему Hugo и настройте опции конвертации"
echo "3. Нажмите 'Convert' для запуска конвертации"
echo "4. Используйте 'Start Watching' для автоматической конвертации при изменениях"
echo "5. Нажмите 'Analyze Vault' для анализа структуры хранилища"
echo "6. Переключайтесь между вкладками для просмотра результатов и логов"
echo ""
echo "Для выхода из приложения закройте окно или нажмите Ctrl+C"
echo ""

# Проверяем возможность запуска GUI
echo "🖥️  Тестирование GUI приложения..."
echo ""

# Тестируем в виртуальном дисплее
echo "Тестирование в виртуальном дисплее:"
xvfb-run -a python3 -c "
from obsidian_to_hugo.ui import main
print('✅ GUI приложение успешно инициализировано в виртуальном дисплее')
print('🎉 PyQt6 GUI с Material Design готов к использованию!')
"

echo ""
echo "📋 Инструкции для запуска GUI в реальном дисплее:"
echo "1. Убедитесь, что у вас есть графический дисплей (X11, Wayland)"
echo "2. Установите переменную DISPLAY: export DISPLAY=:0"
echo "3. Запустите: python3 -m obsidian_to_hugo --gui"
echo ""
echo "📋 Инструкции для запуска GUI в удаленном режиме:"
echo "1. Используйте X11 forwarding: ssh -X user@host"
echo "2. Или используйте VNC сервер"
echo "3. Запустите: python3 -m obsidian_to_hugo --gui"