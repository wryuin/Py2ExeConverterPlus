import os
import sys
import argparse
import subprocess
import shutil
import time
import json
from pathlib import Path


def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config_path, config):
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def clean_build_dirs():
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)


def build_exe(
    script_path,
    output_name=None,
    icon_path=None,
    onefile=True,
    console=True,
    additional_data=None,
    additional_args=None,
    upx=True,
    version_file=None,
    clean=True,
    config_path=None
):
    if clean:
        clean_build_dirs()
    
    if output_name is None:
        output_name = os.path.splitext(os.path.basename(script_path))[0]
    
    config = {}
    if config_path:
        config = load_config(config_path)
    
    command = ["pyinstaller", "--clean"]
    
    if onefile:
        command.append("--onefile")
    else:
        command.append("--onedir")
    
    if not console:
        command.append("--noconsole")
    
    if icon_path and os.path.exists(icon_path):
        command.extend(["--icon", icon_path])
    
    if version_file and os.path.exists(version_file):
        command.extend(["--version-file", version_file])
    
    if upx:
        command.append("--upx-dir=upx")
    
    command.extend(["--name", output_name])
    
    if additional_data:
        for src, dest in additional_data:
            command.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
    
    if additional_args:
        command.extend(additional_args)
    
    command.append(script_path)
    
    start_time = time.time()
    
    try:
        subprocess.run(command, check=True)
        build_time = time.time() - start_time
        
        dist_path = os.path.join("dist", output_name)
        if sys.platform == "win32":
            dist_path += ".exe"
        
        exe_size = os.path.getsize(dist_path) / (1024 * 1024)
        
        print(f"\nСборка завершена успешно: {output_name}")
        print(f"Путь к исполняемому файлу: {os.path.abspath(dist_path)}")
        print(f"Размер файла: {exe_size:.2f} МБ")
        print(f"Время сборки: {build_time:.2f} сек")
        
        if config_path:
            config['last_build'] = {
                'script': script_path,
                'output': output_name,
                'icon': icon_path,
                'onefile': onefile,
                'console': console,
                'size': exe_size,
                'time': build_time,
                'date': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_config(config_path, config)
        
        return dist_path
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Сборка Python-скрипта в исполняемый файл.")
    parser.add_argument("script", help="Путь к Python-скрипту")
    parser.add_argument("--name", help="Имя выходного файла")
    parser.add_argument("--icon", help="Путь к файлу иконки (.ico)")
    parser.add_argument("--dir", action="store_true", help="Создать папку вместо одного файла")
    parser.add_argument("--window", action="store_true", help="Создать оконное приложение (без консоли)")
    parser.add_argument("--data", nargs=2, action="append", metavar=("SRC", "DST"), 
                        help="Дополнительные файлы (SRC DST)")
    parser.add_argument("--sign", action="store_true", help="Подписать исполняемый файл после сборки")
    parser.add_argument("--no-upx", action="store_true", help="Отключить UPX сжатие")
    parser.add_argument("--version-file", help="Путь к файлу версии")
    parser.add_argument("--no-clean", action="store_true", help="Не очищать временные файлы")
    parser.add_argument("--config", help="Путь к файлу конфигурации")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.script):
        print(f"Ошибка: файл {args.script} не найден.")
        return
    
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
        config_path=args.config
    )
    
    if args.sign and exe_path and os.path.exists(exe_path):
        try:
            from signapp import sign_executable
            sign_executable(exe_path)
        except ImportError:
            print("Модуль подписи не найден. Установите его или проверьте файл signapp.py")
        except Exception as e:
            print(f"Ошибка при подписи файла: {e}")


if __name__ == "__main__":
    main()
