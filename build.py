import os
import sys
import argparse
import subprocess
import shutil


def build_exe(
    script_path,
    output_name=None,
    icon_path=None,
    onefile=True,
    console=True,
    additional_data=None,
    additional_args=None,
):
    
    if output_name is None:
        output_name = os.path.splitext(os.path.basename(script_path))[0]
    
    command = ["pyinstaller", "--clean"]
    
    if onefile:
        command.append("--onefile")
    else:
        command.append("--onedir")
    
    if not console:
        command.append("--noconsole")
    
    if icon_path and os.path.exists(icon_path):
        command.extend(["--icon", icon_path])
    
    command.extend(["--name", output_name])
    
    if additional_data:
        for src, dest in additional_data:
            command.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
    
    if additional_args:
        command.extend(additional_args)
    
    command.append(script_path)
    
    try:
        subprocess.run(command, check=True)
        print(f"\nСборка завершена успешно: {output_name}")
        
        dist_path = os.path.join("dist", output_name)
        if sys.platform == "win32":
            dist_path += ".exe"
        
        print(f"Путь к исполняемому файлу: {os.path.abspath(dist_path)}")
        
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
        additional_data=args.data
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
