#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-./circt}"
REPO_URL="${CIRCT_REPO_URL:-https://github.com/llvm/circt.git}"
REF="${CIRCT_REF:-main}"

if [ -e "$TARGET_DIR" ]; then
  echo "Target already exists: $TARGET_DIR" >&2
  exit 1
fi

git clone --branch "$REF" "$REPO_URL" "$TARGET_DIR"
git -C "$TARGET_DIR" submodule update --init --recursive
git -C "$TARGET_DIR" fetch --tags

echo "CIRCT cloned into $TARGET_DIR"
