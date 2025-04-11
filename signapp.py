import os
import sys
import subprocess
import argparse


def sign_executable(
    executable_path,
    cert_path=None,
    cert_password=None,
    timestamp_server="http://timestamp.digicert.com",
    description=None
):
    """
    Подписывает исполняемый файл с использованием signtool для Windows
    или аналогичных инструментов для других платформ.
    """
    if not os.path.exists(executable_path):
        raise FileNotFoundError(f"Исполняемый файл не найден: {executable_path}")

    if sys.platform != "win32":
        print("Подпись файлов поддерживается только в Windows")
        return False

    signtool_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Windows Kits\10\bin\x64\signtool.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Windows Kits\10\bin\x86\signtool.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Windows Kits\8.1\bin\x64\signtool.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Windows Kits\8.1\bin\x86\signtool.exe"),
    ]

    signtool_path = None
    for path in signtool_paths:
        if os.path.exists(path):
            signtool_path = path
            break

    if not signtool_path:
        print("ОШИБКА: SignTool не найден. Установите Windows SDK")
        return False

    command = [signtool_path, "sign"]
    
    if cert_path:
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Файл сертификата не найден: {cert_path}")
        command.extend(["/f", cert_path])
        
        if cert_password:
            command.extend(["/p", cert_password])
    else:
        command.append("/a")
    
    if timestamp_server:
        command.extend(["/tr", timestamp_server, "/td", "sha256"])
    
    if description:
        command.extend(["/d", description])
    
    command.extend(["/fd", "sha256"])
    
    command.append(executable_path)
    
    try:
        print(f"Запуск подписи файла: {executable_path}")
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Подпись успешно выполнена")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ОШИБКА при подписи: {e}")
        print(f"Вывод: {e.stdout}\n{e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Подпись исполняемого файла")
    parser.add_argument("executable", help="Путь к исполняемому файлу")
    parser.add_argument("--cert", help="Путь к файлу сертификата (.pfx)")
    parser.add_argument("--password", help="Пароль для сертификата")
    parser.add_argument("--timestamp", default="http://timestamp.digicert.com", 
                        help="URL сервера меток времени")
    parser.add_argument("--description", help="Описание подписи")
    
    args = parser.parse_args()
    
    sign_executable(
        executable_path=args.executable,
        cert_path=args.cert,
        cert_password=args.password,
        timestamp_server=args.timestamp,
        description=args.description
    )


if __name__ == "__main__":
    main()
