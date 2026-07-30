#!/bin/bash
# Script to build a Debian package (.deb) for OmniGet
set -e

# Define directories
BUILD_DIR="build_deb"
DEB_FILE="omniget_1.0.0_amd64.deb"

echo "=== Memulai Pembuatan Paket Debian OmniGet ==="

# Clean old builds
rm -rf "$BUILD_DIR"
rm -f "$DEB_FILE"

# Create directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/omniget"
mkdir -p "$BUILD_DIR/lib/systemd/system"

# 1. Copy application files (excluding temporary/cache files)
echo "1. Menyalin berkas aplikasi..."
cp -r app.py config.py requirements.txt "$BUILD_DIR/usr/share/omniget/"
cp -r core routes static templates "$BUILD_DIR/usr/share/omniget/"

# Clean up pycache files from the build directory
find "$BUILD_DIR/usr/share/omniget" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 2. Create control file
echo "2. Membuat berkas kontrol (DEBIAN/control)..."
cat << 'EOF' > "$BUILD_DIR/DEBIAN/control"
Package: omniget
Version: 1.0.0
Section: web
Priority: optional
Architecture: amd64
Depends: python3, python3-venv, python3-pip, ffmpeg, aria2
Maintainer: TeknoGenX <support@teknogenx.com>
Description: OmniGet - Universal Media Downloader & P2P Torrent Client
 OmniGet adalah aplikasi web pengunduh media serbaguna berbasis Python Flask
 dengan visual premium Glassmorphism. Mendukung pengunduhan video/audio HD,
 torrent P2P (aria2c), dan site grabbing media secara massal.
EOF

# 3. Create postinst script (Post-Installation)
echo "3. Membuat berkas postinst..."
cat << 'EOF' > "$BUILD_DIR/DEBIAN/postinst"
#!/bin/bash
set -e

# Create omniget system user if it doesn't exist
if ! id "omniget" &>/dev/null; then
    useradd -r -s /bin/false omniget
fi

# Create downloads directory in /var/lib/omniget
mkdir -p /var/lib/omniget/downloads
chown -R omniget:omniget /var/lib/omniget

# Set up virtual environment in /usr/share/omniget/venv
echo "Membuat virtual environment di /usr/share/omniget/venv..."
python3 -m venv /usr/share/omniget/venv
/usr/share/omniget/venv/bin/pip install --upgrade pip
/usr/share/omniget/venv/bin/pip install -r /usr/share/omniget/requirements.txt

# Symlink downloads directory if not already symlinked
if [ ! -L /usr/share/omniget/downloads ]; then
    rm -rf /usr/share/omniget/downloads
    ln -s /var/lib/omniget/downloads /usr/share/omniget/downloads
fi

# Fix ownership
chown -R omniget:omniget /usr/share/omniget

# Reload systemd and start service
echo "Mengaktifkan dan menjalankan service omniget..."
systemctl daemon-reload
systemctl enable omniget.service
systemctl restart omniget.service || true

echo "=========================================================="
echo " OmniGet Berhasil Dipasang!"
echo " Silakan buka http://localhost:5000 di browser Anda."
echo "=========================================================="
EOF

# 4. Create prerm script (Pre-Removal)
echo "4. Membuat berkas prerm..."
cat << 'EOF' > "$BUILD_DIR/DEBIAN/prerm"
#!/bin/bash
set -e

echo "Menghentikan service omniget..."
systemctl stop omniget.service || true
systemctl disable omniget.service || true

# Remove symlink and virtual environment
rm -rf /usr/share/omniget/venv
rm -f /usr/share/omniget/downloads
EOF

# 5. Create postrm script (Post-Removal)
echo "5. Membuat berkas postrm..."
cat << 'EOF' > "$BUILD_DIR/DEBIAN/postrm"
#!/bin/bash
set -e

if [ "$1" = "purge" ]; then
    echo "Membersihkan berkas data omniget..."
    userdel omniget || true
    rm -rf /var/lib/omniget
    rm -rf /usr/share/omniget
    systemctl daemon-reload
fi
EOF

# 6. Create systemd service file
echo "6. Membuat berkas service systemd..."
cat << 'EOF' > "$BUILD_DIR/lib/systemd/system/omniget.service"
[Unit]
Description=OmniGet Media Downloader Service
After=network.target

[Service]
Type=simple
User=omniget
Group=omniget
WorkingDirectory=/usr/share/omniget
ExecStart=/usr/share/omniget/venv/bin/python app.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 7. Create command-line launcher bin
echo "7. Membuat berkas peluncur (bin/omniget)..."
cat << 'EOF' > "$BUILD_DIR/usr/bin/omniget"
#!/bin/bash
echo "Membuka OmniGet di browser..."
xdg-open http://localhost:5000 || sensible-browser http://localhost:5000 || echo "Silakan buka http://localhost:5000 di browser Anda."
EOF

# Set permissions
echo "8. Mengatur perizinan berkas (permissions)..."
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/DEBIAN/prerm"
chmod 755 "$BUILD_DIR/DEBIAN/postrm"
chmod 755 "$BUILD_DIR/usr/bin/omniget"

# Build Debian package
echo "9. Membangun paket .deb menggunakan dpkg-deb..."
dpkg-deb --build "$BUILD_DIR" "$DEB_FILE"

# Cleanup build directory
echo "10. Membersihkan direktori temporer build..."
rm -rf "$BUILD_DIR"

echo "=== Selesai! Paket Debian berhasil dibangun: $DEB_FILE ==="
