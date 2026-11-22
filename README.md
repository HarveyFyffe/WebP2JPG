# webp2jpg

Batch-convert `.webp` images to `.jpg` from the terminal, and optionally convert new downloads automatically in the background.

Works on **Fedora**, **Ubuntu**, **Debian**, **Arch Linux**, and other systemd-based distros.

## Features

- Recursively converts every `.webp` in `~/Downloads` and `~/Pictures` (or any folder you choose)
- Replaces the originals by default, but only after the `.jpg` is written successfully
- Safe preview mode (`--dry-run`)
- Never overwrites an existing `.jpg`
- Handles transparency (see through areas become white)
- Optional systemd watcher that converts new downloads automatically

## Requirements

- Python 3
- [Pillow](https://python-pillow.org/) with WebP support

Install Pillow with your distro's package manager:

| Distro | Command |
| --- | --- |
| Fedora | `sudo dnf install python3-pillow` |
| Ubuntu / Debian | `sudo apt install python3-pil` |
| Arch Linux | `sudo pacman -S python-pillow` |

> **Note:** On recent Debian, Ubuntu and Arch releases, `pip install Pillow` outside a virtual environment is blocked by the system (PEP 668). Use the package above, or install in a virtual environment or with `pipx`.

## Install

```bash
git clone https://github.com/YOUR-USERNAME/webp2jpg.git
cd webp2jpg
chmod +x webp2jpg.py
```

You can run the script straight from the repo folder, or copy it somewhere on your `PATH`:

```bash
mkdir -p ~/.local/bin
cp webp2jpg.py ~/.local/bin/
```

## Usage

Preview first (changes nothing):

```bash
python3 webp2jpg.py --dry-run
```

Then convert for real:

```bash
python3 webp2jpg.py
```

| Option | What it does |
| --- | --- |
| `--dry-run` | Shows what would happen, changes nothing |
| `--keep-originals` | Keeps the `.webp` files after converting |
| `--quality 95` | JPG quality from 1 to 100 (default 90) |
| `FOLDER ...` | Searches the given folders instead of `~/Downloads` and `~/Pictures` |

> **Warning:** By default the original `.webp` files are deleted after conversion and do **not** go to the Trash. Use `--dry-run` first, or `--keep-originals` if unsure.

## Convert automatically on download

This uses a systemd **user** service, so no root access is needed. Make sure `webp2jpg.py` is installed at `~/.local/bin/` (see Install above), then run:

**1. Create the service**

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/webp2jpg.service << 'EOF'
[Unit]
Description=Convert WebP downloads to JPG

[Service]
Type=oneshot
ExecStartPre=/usr/bin/env sleep 2
ExecStart=/usr/bin/env python3 %h/.local/bin/webp2jpg.py %h/Downloads
EOF
```

**2. Create the folder watcher**

```bash
cat > ~/.config/systemd/user/webp2jpg.path << 'EOF'
[Unit]
Description=Watch Downloads for new files

[Path]
PathChanged=%h/Downloads
TriggerLimitIntervalSec=0

[Install]
WantedBy=default.target
EOF
```

**3. Enable it**

```bash
systemctl --user daemon-reload
systemctl --user enable --now webp2jpg.path
```

Any `.webp` you download is now converted a couple of seconds later, and the watcher starts automatically at every login.

### Customising

- **Keep originals:** add `--keep-originals` to the end of the `ExecStart` line.
- **Watch more folders:** add another `PathChanged=%h/Pictures` line under `[Path]`, and add `%h/Pictures` after `%h/Downloads` in `ExecStart`.
- **Different Downloads folder** (for example on a non-English system): replace `%h/Downloads` with your real path. Run `xdg-user-dir DOWNLOAD` to find it.
- After editing any unit file, run `systemctl --user daemon-reload`.

### Managing the watcher

| Task | Command |
| --- | --- |
| Check status | `systemctl --user status webp2jpg.path` |
| View logs and errors | `journalctl --user -u webp2jpg.service` |
| Turn off | `systemctl --user disable --now webp2jpg.path` |
| Turn on | `systemctl --user enable --now webp2jpg.path` |

## Uninstall

```bash
systemctl --user disable --now webp2jpg.path
rm ~/.config/systemd/user/webp2jpg.service ~/.config/systemd/user/webp2jpg.path
rm ~/.local/bin/webp2jpg.py
systemctl --user daemon-reload
```

## Notes

- Browsers download to a temporary file (such as `.part` or `.crdownload`) and rename it when finished. The script only matches finished `.webp` files, so half-downloaded files are safe.
- If a `.jpg` with the same name already exists, that file is skipped and its `.webp` is left alone.
- Animated WebPs keep only their first frame.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Pillow is not installed` | Install it using the table in [Requirements](#requirements) |
| Nothing converts automatically | Run the status command above, then check the logs |
| `~/.local/bin` is not found when running `webp2jpg.py` by name | Run it with `python3 ~/.local/bin/webp2jpg.py`, or add `~/.local/bin` to your `PATH` |
| Watcher stops after logout | Run `loginctl enable-linger $USER` to keep user services running |
