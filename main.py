#!/usr/bin/env python3
"""
Generador de codis QR amb llibreries.
Desa el QR a la carpeta Descarregues i el copia al portaretalls.

Llibreries necessàries:
    pip install qrcode[pil] pillow pyperclip
"""

import sys
import os
import io
import subprocess
import platform

def install_if_missing(packages):
    """Instal·la automàticament les llibreries que faltin."""
    import importlib
    for pkg, import_name in packages:
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"  Instal·lant '{pkg}'...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "-q"],
                check=True
            )

# ─────────────────────────────────────────────
#  PORTARETALLS — multiplataforma sense pyperclip
# ─────────────────────────────────────────────

def copy_image_to_clipboard(image):
    """
    Copia la imatge PIL al portaretalls de forma nativa
    segons el sistema operatiu.
    """
    sistema = platform.system()

    if sistema == "Darwin":  # macOS
        # Convertim a PNG en memòria i usem osascript / pbcopy
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        png_bytes = buf.getvalue()
        try:
            proc = subprocess.Popen(
                ["osascript", "-e",
                'set the clipboard to (read (POSIX file "/dev/stdin") as «class PNGf»)'],
                stdin=subprocess.PIPE
            )
            proc.communicate(input=png_bytes)
            return True, "macOS (osascript)"
        except Exception:
            pass
        # Alternativa: AppleScript via pbcopy (text del path)
        return False, "No s'ha pogut copiar la imatge al portaretalls de macOS."

    elif sistema == "Windows":
        try:
            import win32clipboard
            from PIL import Image
            buf = io.BytesIO()
            image.convert("RGB").save(buf, format="BMP")
            bmp_data = buf.getvalue()[14:]  # Eliminem la capçalera de fitxer BMP
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
            win32clipboard.CloseClipboard()
            return True, "Windows (win32clipboard)"
        except ImportError:
            pass
        # Alternativa via PowerShell
        try:
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            ps_script = (
                "$bytes = [System.IO.File]::ReadAllBytes('%s');"
                "$ms = New-Object System.IO.MemoryStream(,$bytes);"
                "$img = [System.Drawing.Image]::FromStream($ms);"
                "[System.Windows.Forms.Clipboard]::SetImage($img)"
            )
            tmp = os.path.join(os.environ.get("TEMP", "."), "_qr_tmp.png")
            image.save(tmp, format="PNG")
            subprocess.run(
                ["powershell", "-Command",
                f"Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
                f"$img=[System.Drawing.Image]::FromFile('{tmp}');"
                f"[System.Windows.Forms.Clipboard]::SetImage($img)"],
                capture_output=True
            )
            os.remove(tmp)
            return True, "Windows (PowerShell)"
        except Exception as e:
            return False, f"Windows: {e}"

    else:  # Linux
        # Intentem xclip, xsel o wl-copy (Wayland)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        for cmd in [
            ["xclip", "-selection", "clipboard", "-t", "image/png"],
            ["xsel",  "--clipboard", "--input"],
            ["wl-copy", "--type", "image/png"],
        ]:
            try:
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
                proc.communicate(input=png_bytes)
                if proc.returncode == 0:
                    return True, cmd[0]
            except FileNotFoundError:
                continue

        return False, (
            "Linux: cal instal·lar xclip, xsel o wl-copy.\n"
            "    sudo apt install xclip   # Debian/Ubuntu\n"
            "    sudo dnf install xclip   # Fedora"
        )


# ─────────────────────────────────────────────
#  FLUX PRINCIPAL
# ─────────────────────────────────────────────

def main():
    print("=" * 54)
    print("                GENERADOR DE CODIS QR")
    print("=" * 54)

    # Instal·lació automàtica de dependències
    try:
        install_if_missing([
            ("qrcode[pil]", "qrcode"),
            ("pillow",       "PIL"),
            ("pywin32",      "win32clipboard"),
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error instal·lant dependències: {e}")
        print("Executeu manualment:  pip install qrcode[pil] pillow")
        sys.exit(1)

    import qrcode
    from PIL import Image

    # Entrada de text
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(f"\nText rebut per argument: {text}")
    else:
        print("\nIntroduïu l'URL o text per codificar:")
        text = input("  → ").strip()
        if not text:
            print("Error: no heu introduït cap text.")
            sys.exit(1)

    # Carpeta de descàrregues
    home = os.path.expanduser("~")
    for name in ["Descarregues", "Descargas", "Downloads", "downloads"]:
        downloads = os.path.join(home, name)
        if os.path.isdir(downloads):
            break
    else:
        downloads = home

    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in text[:40])
    output_path = os.path.join(downloads, f"qr_{safe}.png")

    # Generar QR
    print(f"\nGenerant codi QR...")
    qr = qrcode.QRCode(
        version=None,           # tria la versió mínima automàticament
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,            # píxels per mòdul
        border=4,               # zona quiet (mòduls blancs)
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Desar
    img.save(output_path, format="PNG")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"  ✓ Fitxer desat: {output_path}  ({size_kb:.1f} KB)")

    # Obrir el fitxer de la imatge
    try:
        os.startfile(output_path)
    except Exception as e:
        print(f"  ⚠ No s'ha pogut obrir el fitxer: {e}")

    # Copiar al portaretalls
    ok, info = copy_image_to_clipboard(img)
    if ok:
        print(f"  ✓ Imatge copiada al portaretalls ({info})")
    else:
        print(f"  ⚠ No s'ha pogut copiar: {info}")
        print(f"  Podeu obrir el fitxer manualment: {output_path}")



if __name__ == "__main__":
    main()