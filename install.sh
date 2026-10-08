#!/usr/bin/env bash
#
# install.sh - Installer for autumn-cat-cursors theme
# Supports user-level and system-wide installation on Linux (GNOME/X11/Wayland/KDE)
#

set -e

THEME_NAME="autumn-cat-cursors"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_THEME="${SCRIPT_DIR}/dist/${THEME_NAME}"
USER_ICONS_DIR="${HOME}/.local/share/icons"
LEGACY_ICONS_DIR="${HOME}/.icons"
SYSTEM_ICONS_DIR="/usr/share/icons"

print_help() {
  echo "Usage: ./install.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --user       Install for current user only (default: ~/.local/share/icons)"
  echo "  --system     Install system-wide (requires sudo: /usr/share/icons)"
  echo "  --uninstall  Remove theme and restore default cursor"
  echo "  --help       Show this help message"
}

apply_gnome_settings() {
  if command -v gsettings >/dev/null 2>&1; then
    echo "[*] Applying cursor theme to GNOME settings..."
    gsettings set org.gnome.desktop.interface cursor-theme "${THEME_NAME}" || true
    echo "[✓] GNOME cursor theme set to '${THEME_NAME}'."
  fi

  # GTK 3 & 4 settings fallback
  for gtk_ver in "gtk-3.0" "gtk-4.0"; do
    config_file="${HOME}/.config/${gtk_ver}/settings.ini"
    mkdir -p "$(dirname "${config_file}")"
    if [ -f "${config_file}" ]; then
      if grep -q "gtk-cursor-theme-name" "${config_file}"; then
        sed -i "s/gtk-cursor-theme-name=.*/gtk-cursor-theme-name=${THEME_NAME}/" "${config_file}"
      else
        echo "gtk-cursor-theme-name=${THEME_NAME}" >> "${config_file}"
      fi
    else
      cat << EOF > "${config_file}"
[Settings]
gtk-cursor-theme-name=${THEME_NAME}
EOF
    fi
  done
}

install_user() {
  echo "[*] Installing '${THEME_NAME}' to ${USER_ICONS_DIR}/${THEME_NAME}..."
  mkdir -p "${USER_ICONS_DIR}"
  rm -rf "${USER_ICONS_DIR}/${THEME_NAME}"
  cp -r "${DIST_THEME}" "${USER_ICONS_DIR}/${THEME_NAME}"

  # Backward compatibility symlink in ~/.icons
  mkdir -p "${LEGACY_ICONS_DIR}"
  rm -rf "${LEGACY_ICONS_DIR}/${THEME_NAME}"
  ln -sfn "${USER_ICONS_DIR}/${THEME_NAME}" "${LEGACY_ICONS_DIR}/${THEME_NAME}"

  apply_gnome_settings
  echo "[✓] Installation completed successfully!"
}

install_system() {
  echo "[*] Installing system-wide to ${SYSTEM_ICONS_DIR}/${THEME_NAME}..."
  sudo rm -rf "${SYSTEM_ICONS_DIR}/${THEME_NAME}"
  sudo cp -r "${DIST_THEME}" "${SYSTEM_ICONS_DIR}/${THEME_NAME}"
  sudo chmod -R a+rX "${SYSTEM_ICONS_DIR}/${THEME_NAME}"
  
  if command -v update-alternatives >/dev/null 2>&1; then
    sudo update-alternatives --install /usr/share/icons/default/index.theme x-cursor-theme "${SYSTEM_ICONS_DIR}/${THEME_NAME}/cursor.theme" 110 || true
    sudo update-alternatives --set x-cursor-theme "${SYSTEM_ICONS_DIR}/${THEME_NAME}/cursor.theme" || true
  fi

  install_user
}

uninstall() {
  echo "[*] Uninstalling '${THEME_NAME}'..."
  rm -rf "${USER_ICONS_DIR}/${THEME_NAME}"
  rm -rf "${LEGACY_ICONS_DIR}/${THEME_NAME}"
  if [ -d "${SYSTEM_ICONS_DIR}/${THEME_NAME}" ]; then
    echo "[*] Removing system-wide theme..."
    sudo rm -rf "${SYSTEM_ICONS_DIR}/${THEME_NAME}" || true
  fi

  if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface cursor-theme 'Yaru' || true
  fi
  echo "[✓] Uninstalled. Restored cursor theme to 'Yaru'."
}

# Ensure precompiled theme exists
if [ ! -d "${DIST_THEME}" ]; then
  echo "[*] Theme binaries not found. Building with build.py..."
  python3 "${SCRIPT_DIR}/build.py"
fi

MODE="${1:---user}"

case "${MODE}" in
  --user)
    install_user
    ;;
  --system)
    install_system
    ;;
  --uninstall)
    uninstall
    ;;
  --help|-h)
    print_help
    ;;
  *)
    echo "Unknown option: ${MODE}"
    print_help
    exit 1
    ;;
esac

