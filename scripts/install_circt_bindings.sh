#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path-to-circt-checkout>" >&2
  exit 1
fi

CIRCT_DIR="$(cd "$1" && pwd)"
BUILD_CIRCT_FROM_SOURCE="${BUILD_CIRCT_FROM_SOURCE:-0}"

if [ ! -d "$CIRCT_DIR/lib/Bindings/Python" ]; then
  echo "Expected CIRCT Python bindings at $CIRCT_DIR/lib/Bindings/Python" >&2
  exit 1
fi

if [ "$BUILD_CIRCT_FROM_SOURCE" != "1" ]; then
  cat >&2 <<'EOF'
Refusing full CIRCT source build by default.
Set BUILD_CIRCT_FROM_SOURCE=1 to explicitly allow it (recommended only for base-image creation).
EOF
  exit 2
fi

SKIP_APT_INSTALL="${SKIP_APT_INSTALL:-0}"
CIRCT_BUILD_DIR="${CIRCT_BUILD_DIR:-$CIRCT_DIR/build-python}"
CIRCT_INSTALL_DIR="${CIRCT_INSTALL_DIR:-$CIRCT_DIR/install-python}"

resolve_python_bin() {
  local candidate
  for candidate in \
    "${PYTHON_BIN:-}" \
    "$PWD/.venv/bin/python" \
    "${PYTHON_BIN_FALLBACK:-$HOME/.local/python-3.14t/bin/python3.14t}" \
    python3.14t \
    python3 \
    python
  do
    if [ -z "$candidate" ]; then
      continue
    fi
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done

  return 1
}

PYTHON_BIN_RESOLVED="$(resolve_python_bin || true)"
if [ -z "$PYTHON_BIN_RESOLVED" ]; then
  echo "No usable Python found. Run scripts/setup_env.sh first or set PYTHON_BIN." >&2
  exit 1
fi
PYTHON_BIN="$PYTHON_BIN_RESOLVED"

install_build_deps() {
  if [ "$SKIP_APT_INSTALL" = "1" ]; then
    return
  fi

  if command -v apt-get >/dev/null 2>&1; then
    local sudo_cmd=""
    if command -v sudo >/dev/null 2>&1; then
      sudo_cmd="sudo"
    fi
    $sudo_cmd apt-get update
    $sudo_cmd apt-get install -y --no-install-recommends \
      build-essential \
      g++ \
      libstdc++-13-dev \
      git \
      cmake \
      ninja-build \
      python3-dev \
      curl
  fi
}

if git -C "$CIRCT_DIR" rev-parse --is-shallow-repository | rg -q '^true$'; then
  git -C "$CIRCT_DIR" fetch --unshallow --tags || git -C "$CIRCT_DIR" fetch --tags
else
  git -C "$CIRCT_DIR" fetch --tags || true
fi

git -C "$CIRCT_DIR" submodule update --init --recursive

install_build_deps

"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
"$PYTHON_BIN" -m pip install nanobind pyyaml numpy pybind11

LLVM_VC_REPOSITORY="${LLVM_FORCE_VC_REPOSITORY:-$(git -C "$CIRCT_DIR/llvm" config --get remote.origin.url || true)}"
LLVM_VC_REPOSITORY="$(printf '%s' "$LLVM_VC_REPOSITORY" | sed -E 's#https?://[^/@]+@#https://#')"
if [ -z "$LLVM_VC_REPOSITORY" ]; then
  LLVM_VC_REPOSITORY="https://github.com/llvm/llvm-project"
fi

PYTHON_PREFIX="$($PYTHON_BIN -c 'import sys; print(sys.base_prefix)')"

CC_BIN="${CC:-$(command -v gcc || true)}"
CXX_BIN="${CXX:-$(command -v g++ || true)}"

cmake \
  -S "$CIRCT_DIR/llvm/llvm" \
  -B "$CIRCT_BUILD_DIR" \
  -G "${CMAKE_GENERATOR:-Ninja}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$CIRCT_INSTALL_DIR" \
  -DLLVM_ENABLE_PROJECTS=mlir \
  -DLLVM_EXTERNAL_PROJECTS=circt \
  -DLLVM_EXTERNAL_CIRCT_SOURCE_DIR="$CIRCT_DIR" \
  -DLLVM_TARGETS_TO_BUILD=host \
  -DMLIR_ENABLE_BINDINGS_PYTHON=ON \
  -DCIRCT_BINDINGS_PYTHON_ENABLED=ON \
  -DPython_ROOT_DIR="$PYTHON_PREFIX" \
  -DPython_EXECUTABLE="$PYTHON_BIN" \
  -DPython3_ROOT_DIR="$PYTHON_PREFIX" \
  -DPython3_EXECUTABLE="$PYTHON_BIN" \
  -DLLVM_FORCE_VC_REPOSITORY="$LLVM_VC_REPOSITORY" \
  ${CC_BIN:+-DCMAKE_C_COMPILER="$CC_BIN"} \
  ${CXX_BIN:+-DCMAKE_CXX_COMPILER="$CXX_BIN"}

cmake --build "$CIRCT_BUILD_DIR" --target install-CIRCTPythonModules -- -j"$(nproc)"

PYTHON_SITE_PACKAGES="$($PYTHON_BIN -c 'import site; print(site.getsitepackages()[0])')"
mkdir -p "$PYTHON_SITE_PACKAGES"
printf '%s\n' "$CIRCT_INSTALL_DIR/python_packages/circt_core" > "$PYTHON_SITE_PACKAGES/circt_local.pth"

"$PYTHON_BIN" -c 'import circt; print("CIRCT import OK")'
