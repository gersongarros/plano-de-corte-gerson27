#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_ID=br.com.gerson27.planodecorte
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
APPDIR="$DATA/plano-corte-gerson27"
DESKTOP="$DATA/applications/$APP_ID.desktop"
ICONS="$DATA/icons/hicolor"
if ! /usr/bin/python3 -c "import gi, cairo; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk"; then
    echo 'Instale as dependências e execute novamente:'
    echo 'sudo dnf install python3-gobject gtk4 python3-cairo'
    exit 1
fi
for f in plano_corte.py otimizador.py icone.png; do
    test -s "$DIR/$f" || { echo "Arquivo ausente: $f"; exit 1; }
done
BACKUP="$DATA/plano-corte-gerson27-backups/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$BACKUP" "$APPDIR" "$(dirname "$DESKTOP")" "$ICONS/512x512/apps"
if test -d "$APPDIR"; then cp -a "$APPDIR" "$BACKUP/app"; fi
if test -f "$DESKTOP"; then cp -a "$DESKTOP" "$BACKUP/launcher.desktop"; fi
if test -f "$ICONS/scalable/apps/$APP_ID.svg"; then
    cp -a "$ICONS/scalable/apps/$APP_ID.svg" "$BACKUP/icone-anterior.svg"
    rm -- "$ICONS/scalable/apps/$APP_ID.svg"
fi
if test -f "$ICONS/512x512/apps/$APP_ID.png"; then
    cp -a "$ICONS/512x512/apps/$APP_ID.png" "$BACKUP/icone-anterior.png"
fi
install -m 644 "$DIR/plano_corte.py" "$DIR/otimizador.py" "$DIR/icone.png" "$APPDIR/"
# O mesmo nome no tema, na janela GTK e no lançador Wayland.
install -m 644 "$DIR/icone.png" "$ICONS/512x512/apps/$APP_ID.png"
cat > "$APPDIR/iniciar.sh" <<'EOF'
#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
exec /usr/bin/python3 plano_corte.py "$@"
EOF
chmod 755 "$APPDIR/iniciar.sh"
/usr/bin/python3 - "$DESKTOP" "$APPDIR/iniciar.sh" <<'PY'
from pathlib import Path
import sys
exe = sys.argv[2].replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
Path(sys.argv[1]).write_text(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Plano de Corte Gerson27
Comment=Otimizador de cortes guilhotina para chapas de MDF e compensado
Exec="{exe}"
Icon=br.com.gerson27.planodecorte
Terminal=false
Categories=Graphics;Engineering;
StartupNotify=true
StartupWMClass=br.com.gerson27.planodecorte
''')
PY
chmod 644 "$DESKTOP"
if command -v gtk-update-icon-cache >/dev/null; then gtk-update-icon-cache -f -t "$ICONS" || true; fi
if command -v update-desktop-database >/dev/null; then update-desktop-database "$DATA/applications" || true; fi
printf '\nPlano de Corte Gerson27 v1.1.2 instalado.\nBackup: %s\nFeche a janela antiga após salvar e abra novamente pelo menu de aplicativos.\n' "$BACKUP"
