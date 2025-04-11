# Python to EXE Converter

A set of scripts for converting Python scripts to executable (.exe) files with digital signature support.

## Project Files

- `build.py` - Main build script using PyInstaller
- `signapp.py` - Utility for signing .exe files (Windows only)
- `test.py` - Test script for build system verification

## Requirements

- Python 3.6 or higher
- PyInstaller (`pip install pyinstaller`)
- Windows SDK (for file signing)

## Usage

### Basic Build

```bash
# Basic application build
python build.py path_to_script.py

# Example with test script
python build.py test.py
```

### Additional Options

```bash
# Set output filename
python build.py test.py --name MyApp

# Set icon
python build.py test.py --icon path/to/icon.ico

# Create window application (no console)
python build.py test.py --window

# Create directory instead of single file
python build.py test.py --dir

# Add additional files/resources
python build.py test.py --data file.txt resources/

# Sign after build (requires Windows SDK)
python build.py test.py --sign

# Disable UPX compression
python build.py test.py --no-upx

# Add version information
python build.py test.py --version-file version.txt

# Save build configuration
python build.py test.py --config build_config.json

# Skip temporary files cleanup
python build.py test.py --no-clean
```

### File Signing Only

```bash
# Sign existing .exe
python signapp.py path/to/app.exe

# Sign with certificate
python signapp.py path/to/app.exe --cert certificate.pfx --password password

# Additional signing options
python signapp.py path/to/app.exe --description "My Application" --timestamp http://timestamp.digicert.com
```

## Examples

1. Create simple application:
   ```bash
   python build.py test.py
   ```

2. Create window application with icon:
   ```bash
   python build.py app.py --name MyApp --icon icons/app.ico --window
   ```

3. Build and sign in one command:
   ```bash
   python build.py app.py --name SignedApp --sign
   ```

4. Build with version info and UPX compression:
   ```bash
   python build.py app.py --version-file version.txt
   ```

5. Build with configuration saving:
   ```bash
   python build.py app.py --config build_config.json
   ```

## Notes

- Scripts are designed with minimalism - simple and easily configurable
- Build creates files in `dist/` directory
- PyInstaller temporary files are in `build/` directory
- Windows SDK with signtool.exe is required for signing
- Build statistics (size, time) are saved in configuration file if specified
- UPX compression can be disabled with `--no-upx` option
- Version information can be added using `--version-file` option
