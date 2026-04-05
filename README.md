# QR Code Generator

This project is a simple tool to generate QR codes from text or URLs and save them to the downloads folder.

It also attempts to copy the generated image to the system clipboard automatically.

## Features

- Generates a PNG file containing the QR code.
- Saves the QR image to the downloads folder (`Descarregues`, `Descargas`, `Downloads` or similar).
- Copies the image to the clipboard when possible.
- Automatically installs missing Python dependencies.

## Requirements

- Python 3.7 or newer
- Python packages:
  - `qrcode[pil]`
  - `pillow`
  - `pywin32` (Windows only, required for clipboard support via `win32clipboard`)

## Installation

```bash
pip install qrcode[pil] pillow pyperclip
```

> Note: the script may also try to install missing libraries automatically if they are not already present.

## Usage

Run the script with Python:

```bash
python main.py
```

You can also pass the text or URL as command-line arguments:

```bash
python main.py https://example.com
```

If no argument is provided, the script will ask you to enter text manually.

## How it works

1. Checks for missing dependencies and installs them.
2. Generates the QR code using `qrcode` and `Pillow`.
3. Saves the image to the downloads folder.
4. Attempts to copy the image to the system clipboard.

## Notes

- On Windows, clipboard copying can work with `win32clipboard` or PowerShell.
- On Linux, `xclip`, `xsel`, or `wl-copy` must be installed to copy the image to the clipboard.
- If the QR code cannot be copied to the clipboard, the PNG file will still be saved.

## View the project
To save it locally, you can download the latest version from GitHub.

QR code generator © 2026 by <a href="https://arnautm-dev.netlify.app">Arnau TM.</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International</a><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">