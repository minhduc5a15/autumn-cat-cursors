#!/usr/bin/env python3
"""
build.py - Automated compiler for autumn-cat-cursors theme
Generates multi-resolution Xcursor binaries (24px, 32px, 48px, 64px)
from high-resolution source assets.
"""

import os
import shutil
import subprocess
from PIL import Image

THEME_NAME = "autumn-cat-cursors"
DISPLAY_NAME = "Autumn Cat Cursor"
SIZES = [24, 32, 48, 64]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(SCRIPT_DIR, "dist", THEME_NAME)
CURSORS_DIR = os.path.join(DIST_DIR, "cursors")
TMP_BUILD = os.path.join(SCRIPT_DIR, ".build_tmp")

def calc_hots(base_hx, base_hy):
    return {s: (max(0, int(round(base_hx * s / 48.0))), max(0, int(round(base_hy * s / 48.0)))) for s in SIZES}

STATIC_CURSORS = {
    'default': {
        'src': os.path.join(SCRIPT_DIR, 'original', 'default.png'),
        'hots': calc_hots(6, 2)
    },
    'pointer': {
        'src': os.path.join(SCRIPT_DIR, 'original', 'pointer.png'),
        'hots': calc_hots(16, 2)
    },
    'text': {
        'src': os.path.join(SCRIPT_DIR, 'original', 'text.png'),
        'hots': {s: (s // 2, s // 2) for s in SIZES}
    },
    'crosshair': {
        'src': os.path.join(SCRIPT_DIR, 'original', 'crosshair.png'),
        'hots': calc_hots(24, 23)
    }
}

ANIMATED_CURSORS = {
    'wait': {
        'src': os.path.join(SCRIPT_DIR, 'sprites', 'original', 'wait.png'),
        'hots': {s: (s // 2, s // 2) for s in SIZES},
        'delay': 120
    },
    'progress': {
        'src': os.path.join(SCRIPT_DIR, 'sprites', 'original', 'progress.png'),
        'hots': calc_hots(6, 2),
        'delay': 120
    }
}

SYMLINKS = {
    'default': ['left_ptr', 'arrow', 'top_left_arrow', 'right_ptr'],
    'pointer': ['hand2', 'hand', 'pointing_hand', 'hand1', 'e29285e634086352946a0e7090d73106'],
    'wait': ['watch', '0426c80cad930eee16ad2a542037b77b'],
    'progress': ['left_ptr_watch', 'half-busy', '08e8e1c95fe2fc01f976f1e063a24ccd', '3ecb610c1bf2410f44200f48c40d3599'],
    'text': ['xterm', 'ibeam'],
    'crosshair': ['cross', 'tcross', 'cross_reverse', 'diamond_cross']
}

def main():
    print(f"[*] Building {THEME_NAME} cursor theme...")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(CURSORS_DIR, exist_ok=True)
    os.makedirs(TMP_BUILD, exist_ok=True)

    # 1. Compile static cursors
    for name, data in STATIC_CURSORS.items():
        print(f"    Compiling static cursor: {name}")
        cfg_lines = []
        with Image.open(data['src']) as orig:
            for s in SIZES:
                img_s = orig.resize((s, s), Image.Resampling.LANCZOS)
                png_path = os.path.join(TMP_BUILD, f"{name}_{s}.png")
                img_s.save(png_path, format="PNG", optimize=True)
                hx, hy = data['hots'][s]
                cfg_lines.append(f"{s} {hx} {hy} {png_path}")
        
        cfg_path = os.path.join(TMP_BUILD, f"{name}.cursor")
        with open(cfg_path, "w") as f:
            f.write("\n".join(cfg_lines) + "\n")
        subprocess.run(["xcursorgen", cfg_path, os.path.join(CURSORS_DIR, name)], check=True)

    # 2. Compile animated cursors
    for name, data in ANIMATED_CURSORS.items():
        print(f"    Compiling animated cursor: {name}")
        cfg_lines = []
        with Image.open(data['src']) as orig:
            w, h = orig.size
            cols, rows = 4, 2
            cell_w, cell_h = w / cols, h / rows
            for s in SIZES:
                hx, hy = data['hots'][s]
                frame_idx = 0
                for r in range(rows):
                    for c in range(cols):
                        box = (int(round(c * cell_w)), int(round(r * cell_h)),
                               int(round((c + 1) * cell_w)), int(round((r + 1) * cell_h)))
                        frame = orig.crop(box).resize((s, s), Image.Resampling.LANCZOS)
                        png_path = os.path.join(TMP_BUILD, f"{name}_{s}_{frame_idx}.png")
                        frame.save(png_path, format="PNG", optimize=True)
                        cfg_lines.append(f"{s} {hx} {hy} {png_path} {data['delay']}")
                        frame_idx += 1
        
        cfg_path = os.path.join(TMP_BUILD, f"{name}.cursor")
        with open(cfg_path, "w") as f:
            f.write("\n".join(cfg_lines) + "\n")
        subprocess.run(["xcursorgen", cfg_path, os.path.join(CURSORS_DIR, name)], check=True)

    # 3. Create symlinks
    print("    Creating alias symlinks...")
    for target, aliases in SYMLINKS.items():
        for alias in aliases:
            alias_path = os.path.join(CURSORS_DIR, alias)
            if os.path.exists(alias_path) or os.path.islink(alias_path):
                os.remove(alias_path)
            os.symlink(target, alias_path)

    # 4. Generate index.theme & cursor.theme
    index_theme_content = f"""[Icon Theme]
Name={DISPLAY_NAME}
Comment=Cute Cat Frog Autumn Cursor Theme
Inherits=Yaru,Adwaita
"""
    with open(os.path.join(DIST_DIR, "index.theme"), "w") as f:
        f.write(index_theme_content)

    cursor_theme_content = f"""[Icon Theme]
Name={DISPLAY_NAME}
Inherits={THEME_NAME}
"""
    with open(os.path.join(DIST_DIR, "cursor.theme"), "w") as f:
        f.write(cursor_theme_content)

    # Cleanup temporary directory
    shutil.rmtree(TMP_BUILD, ignore_errors=True)
    print(f"[✓] Build complete: {DIST_DIR}")

if __name__ == "__main__":
    main()
