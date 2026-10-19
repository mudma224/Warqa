#!/usr/bin/env bash
# Recupere le code du benchmark DocILE hors depot, a un commit epingle.
# Le clone vit dans ../docile-upstream (en dehors du perimetre du depot Warqa).
set -euo pipefail

PINNED_COMMIT="45f1f00d184664e23b0fb657574ce07b2bfac065"
TARGET_DIR="$(cd "$(dirname "$0")/../.." && pwd)/docile-upstream"

if [ ! -d "$TARGET_DIR" ]; then
  git clone https://github.com/rossumai/docile.git "$TARGET_DIR"
fi
git -C "$TARGET_DIR" fetch -q origin
git -C "$TARGET_DIR" checkout -q "$PINNED_COMMIT"
echo "DocILE pret dans $TARGET_DIR (commit $PINNED_COMMIT)"
