import os
import sys
import argparse
import subprocess
import shutil
import time
import json
import platform
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import importlib.util

# Версии библиотек для обновления
REQUIRED_LIBRARIES = {
    'pyinstaller': '6.7.0',
    'setuptools': '69.5.1'
}

class BuildConfig:
    """Класс для управления конфигурацией сборки"""
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки конфигурации: {e}")
        return {}
    
    def save_config(self):
        """Сохранение конфигурации в файл"""
        if self.config_path:
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False, sort_keys=True)
            except IOError as e:
                print(f"Ошибка сохранения конфигурации: {e}")

# Проверка наличия upx в системе
def is_upx_available() -> bool:
    return shutil.which('upx') is not None

# Проверка и установка зависимостей
def check_dependencies():
    try:
        for package, version in REQUIRED_LIBRARIES.items():
            if importlib.util.find_spec(package) is None:
                print(f"Пакет {package} не найден. Устанавливаю...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'{package}>={version}'])
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', f'{package}>={version}'])
        if not is_upx_available():
            print("Внимание: UPX не найден в системе. Для сжатия исполняемых файлов скачайте UPX с https://upx.github.io/ и добавьте его в PATH.")
    except Exception as e:
        print(f"Ошибка при проверке/установке зависимостей: {e}")

def clean_build_dirs():
    """Очистка временных файлов сборки"""
    dirs_to_clean = ['build', 'dist', '__pycache__', '.cache']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
            except OSError as e:
                print(f"Ошибка при удалении {dir_name}: {e}")
    
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
        except OSError as e:
            print(f"Ошибка при удалении {spec_file}: {e}")

def validate_paths(*paths: str) -> bool:
    """Проверка существования указанных путей"""
    for path in paths:
        if path and not os.path.exists(path):
            print(f"Ошибка: путь не существует - {path}")
            return False
    return True

def get_default_output_name(script_path: str) -> str:
    """Генерация имени выходного файла по умолчанию"""
    return os.path.splitext(os.path.basename(script_path))[0]

def build_exe(
    script_path: str,
    output_name: Optional[str] = None,
    icon_path: Optional[str] = None,
    onefile: bool = True,
    console: bool = True,
    additional_data: Optional[List[Tuple[str, str]]] = None,
    additional_args: Optional[List[str]] = None,
    upx: bool = True,
    version_file: Optional[str] = None,
    clean: bool = True,
    config_path: Optional[str] = None,
    sign: bool = False
) -> Optional[str]:
    """
    Сборка Python-скрипта в исполняемый файл
    
    :param script_path: Путь к Python-скрипту
    :param output_name: Имя выходного файла
    :param icon_path: Путь к файлу иконки
    :param onefile: Собрать в один файл
    :param console: Показывать консоль
    :param additional_data: Дополнительные файлы для включения
    :param additional_args: Дополнительные аргументы PyInstaller
    :param upx: Использовать UPX сжатие
    :param version_file: Файл с информацией о версии
    :param clean: Очистить временные файлы
    :param config_path: Путь к файлу конфигурации
    :param sign: Подписать исполняемый файл
    :return: Путь к собранному файлу или None при ошибке
    """
    # Проверка зависимостей
    check_dependencies()
    
    # Проверка наличия PyInstaller
    if importlib.util.find_spec('PyInstaller') is None:
        print("Ошибка: PyInstaller не установлен. Установите его командой: python -m pip install pyinstaller")
        return None
    
    # Валидация путей
    if not validate_paths(script_path, icon_path, version_file):
        return None
    
    if clean:
        clean_build_dirs()
    
    # Настройка конфигурации
    config = BuildConfig(config_path)
    
    # Определение имени выходного файла
    output_name = output_name or get_default_output_name(script_path)
    
    # Подготовка команды PyInstaller
    command = [
        sys.executable,
        "-m",
        "pyinstaller",
        "--clean",
        "--noconfirm"
    ]
    
    if onefile:
        command.append("--onefile")
    else:
        command.append("--onedir")
    
    if not console:
        command.append("--noconsole")
        if platform.system() == "Windows":
            command.append("--windowed")
    
    if icon_path:
        command.extend(["--icon", os.path.abspath(icon_path)])
    
    if version_file:
        command.extend(["--version-file", os.path.abspath(version_file)])
    
    if upx:
        upx_dir = os.path.join(os.path.dirname(__file__), "upx")
        if os.path.exists(upx_dir):
            command.extend(["--upx-dir", upx_dir])
    
    command.extend(["--name", output_name])
    
    # Добавление дополнительных данных
    if additional_data:
        for src, dest in additional_data:
            if os.path.exists(src):
                command.extend(["--add-data", f"{os.path.abspath(src)}{os.pathsep}{dest}"])
            else:
                print(f"Предупреждение: файл не найден и не будет включен - {src}")
    
    # Добавление дополнительных аргументов
    if additional_args:
        command.extend(additional_args)
    
    command.append(os.path.abspath(script_path))
    
    # Логирование команды
    print("\nВыполняемая команда:")
    print(" ".join(command))
    
    # Замер времени сборки
    start_time = time.perf_counter()
    
    try:
        # Выполнение сборки
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        build_time = time.perf_counter() - start_time
        
        # Определение пути к собранному файлу
        dist_path = os.path.join("dist", output_name)
        if platform.system() == "Windows":
            dist_path += ".exe"
        
        if not os.path.exists(dist_path):
            raise FileNotFoundError(f"Исполняемый файл не найден: {dist_path}")
        
        # Получение информации о файле
        exe_size = os.path.getsize(dist_path) / (1024 * 1024)  # в МБ
        
        print("\n" + "=" * 50)
        print(f"Сборка завершена успешно: {output_name}")
        print(f"Путь к исполняемому файлу: {os.path.abspath(dist_path)}")
        print(f"Размер файла: {exe_size:.2f} МБ")
        print(f"Время сборки: {build_time:.2f} сек")
        print("=" * 50 + "\n")
        
        # Сохранение информации о сборке в конфиг
        config.config['last_build'] = {
            'script': script_path,
            'output': output_name,
            'icon': icon_path,
            'onefile': onefile,
            'console': console,
            'size': exe_size,
            'time': build_time,
            'date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'platform': platform.platform(),
            'python_version': platform.python_version()
        }
        config.save_config()
        
        # Подпись файла если требуется
        if sign:
            sign_executable(dist_path)
        
        return dist_path
    
    except subprocess.CalledProcessError as e:
        print("\nОшибка при сборке:")
        print(e.stderr)
        print(f"\nКоманда завершилась с кодом {e.returncode}")
        return None
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        return None

def sign_executable(exe_path: str):
    """Подпись исполняемого файла"""
    if not os.path.exists(exe_path):
        print(f"Ошибка: файл для подписи не найден - {exe_path}")
        return
    
    print(f"\nПодпись файла: {exe_path}")
    
    # Здесь должна быть реализация подписи
    # Например, с использованием signtool на Windows или codesign на macOS
    try:
        if platform.system() == "Windows":
            # Пример для Windows signtool
            sign_command = [
                "signtool",
                "sign",
                "/fd", "sha256",
                "/tr", "http://timestamp.digicert.com",
                "/td", "sha256",
                "/a",
                exe_path
            ]
            subprocess.run(sign_command, check=True)
        elif platform.system() == "Darwin":
            # Пример для macOS codesign
            sign_command = [
                "codesign",
                "--deep",
                "--force",
                "--verbose",
                "--sign", "Developer ID Application",
                exe_path
            ]
            subprocess.run(sign_command, check=True)
        else:
            print("Подпись не поддерживается для текущей платформы")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при подписи файла: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при подписи: {e}")

def parse_args() -> argparse.Namespace:
    """Разбор аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Сборка Python-скрипта в исполняемый файл",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "script",
        help="Путь к Python-скрипту"
    )
    parser.add_argument(
        "--name",
        help="Имя выходного файла"
    )
    parser.add_argument(
        "--icon",
        help="Путь к файлу иконки (.ico для Windows, .icns для macOS)"
    )
    parser.add_argument(
        "--dir",
        action="store_true",
        help="Создать папку вместо одного файла"
    )
    parser.add_argument(
        "--window",
        action="store_true",
        help="Создать оконное приложение (без консоли)"
    )
    parser.add_argument(
        "--data",
        nargs=2,
        action="append",
        metavar=("SRC", "DST"),
        help="Дополнительные файлы (SRC DST)"
    )
    parser.add_argument(
        "--sign",
        action="store_true",
        help="Подписать исполняемый файл после сборки"
    )
    parser.add_argument(
        "--no-upx",
        action="store_true",
        help="Отключить UPX сжатие"
    )
    parser.add_argument(
        "--version-file",
        help="Путь к файлу версии"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Не очищать временные файлы"
    )
    parser.add_argument(
        "--config",
        help="Путь к файлу конфигурации"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Режим отладки (показывать больше информации)"
    )
    
    return parser.parse_args()

def main():
    """Основная функция"""
    args = parse_args()
    
    if not os.path.exists(args.script):
        print(f"Ошибка: файл {args.script} не найден.")
        return
    
    try:
        exe_path = build_exe(
            script_path=args.script,
            output_name=args.name,
            icon_path=args.icon,
            onefile=not args.dir,
            console=not args.window,
            additional_data=args.data,
            upx=not args.no_upx,
            version_file=args.version_file,
            clean=not args.no_clean,
            config_path=args.config,
            sign=args.sign
        )
        
        if exe_path:
            print(f"Сборка успешно завершена: {exe_path}")
            sys.exit(0)
        else:
            print("Сборка завершена с ошибками")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nСборка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()