#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.14.0}"
PY314T_PREFIX="${PY314T_PREFIX:-$HOME/.local/python-3.14t}"
BUILD_ROOT="${PY314T_BUILD_ROOT:-$HOME/.cache/python314t-build}"

if [ -x "$PY314T_PREFIX/bin/python3.14t" ]; then
  "$PY314T_PREFIX/bin/python3.14t" -VV
  exit 0
fi

install_build_deps() {
  if command -v apt-get >/dev/null 2>&1; then
    local sudo_cmd=""
    if command -v sudo >/dev/null 2>&1; then
      sudo_cmd="sudo"
    fi
    $sudo_cmd apt-get update
    $sudo_cmd apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      ca-certificates \
      xz-utils \
      zlib1g-dev \
      libbz2-dev \
      libffi-dev \
      libgdbm-dev \
      liblzma-dev \
      libncursesw5-dev \
      libreadline-dev \
      libsqlite3-dev \
      libssl-dev \
      libuuid1 \
      uuid-dev \
      tk-dev
  fi
}

install_build_deps

mkdir -p "$BUILD_ROOT"
cd "$BUILD_ROOT"

archive="Python-${PYTHON_VERSION}.tgz"
if [ ! -f "$archive" ]; then
  curl -fsSLO "https://www.python.org/ftp/python/${PYTHON_VERSION}/${archive}"
fi

src_dir="Python-${PYTHON_VERSION}"
rm -rf "$src_dir"
tar -xzf "$archive"
cd "$src_dir"

./configure \
  --prefix="$PY314T_PREFIX" \
  --with-ensurepip=install \
  --disable-gil

make -j"$(nproc)"
make install

ln -sf "$PY314T_PREFIX/bin/python3.14" "$PY314T_PREFIX/bin/python3.14t"
"$PY314T_PREFIX/bin/python3.14t" -VV
