# Python в EXE конвертер

Набор скриптов для простой конвертации Python-скриптов в исполняемые файлы (.exe) с возможностью подписи.

## Файлы проекта

- `build.py` - основной скрипт сборки через PyInstaller
- `signapp.py` - утилита для подписи .exe файлов (для Windows)
- `test.py` - тестовый скрипт для проверки работы системы сборки

## Требования

- Python 3.6 или выше
- PyInstaller (`pip install pyinstaller`)
- Windows SDK (если нужна подпись файлов)

## Использование

### Простая сборка

```bash
# Сборка обычного приложения
python build.py путь_к_скрипту.py

# Пример с тестовым скриптом
python build.py test.py
```

### Дополнительные опции

```bash
# Задать имя выходного файла
python build.py test.py --name МоеПриложение

# Установить иконку
python build.py test.py --icon путь/к/иконке.ico

# Создать оконное приложение (без консоли)
python build.py test.py --window

# Создать папку с файлами вместо одного файла
python build.py test.py --dir

# Добавить дополнительные файлы/ресурсы
python build.py test.py --data файл.txt ресурсы/

# Подписать после сборки (требуется Windows SDK)
python build.py test.py --sign
```

### Только подпись файла

```bash
# Подписывание существующего .exe
python signapp.py путь/к/приложению.exe

# Подписывание с использованием сертификата
python signapp.py путь/к/приложению.exe --cert сертификат.pfx --password пароль

# Дополнительные настройки подписи
python signapp.py путь/к/приложению.exe --description "Мое приложение" --timestamp http://timestamp.digicert.com
```

## Примеры

1. Создание простого приложения:
   ```bash
   python build.py test.py
   ```

2. Создание оконного приложения с иконкой:
   ```bash
   python build.py app.py --name МоеПриложение --icon icons/app.ico --window
   ```

3. Сборка и подпись в одну команду:
   ```bash
   python build.py app.py --name ПодписанноеПриложение --sign
   ```

## Примечания

- Скрипты разработаны с минимализмом - простые и легко настраиваемые
- Сборка создает файлы в папке `dist/`
- Временные файлы PyInstaller находятся в папке `build/`
- Для подписи требуется Windows SDK с утилитой signtool.exe
