#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "Fetching latest for all submodules..."
git submodule update --remote

changed=$(git diff --name-only)

if [ -z "$changed" ]; then
  echo "Already up to date."
  exit 0
fi

echo "Updated:"
echo "$changed"

git add $changed
git commit -m "Update submodules: $(echo $changed | sed 's|raw/||g' | tr ' ' ', ')"

echo "Done."
