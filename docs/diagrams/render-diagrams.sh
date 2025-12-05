#!/bin/bash
# Render all PlantUML diagrams using Kroki
# Usage: ./render-diagrams.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Rendering C4 diagrams..."
curl -s -X POST https://kroki.io/c4plantuml/png \
  -H "Content-Type: text/plain" \
  --data-binary @c4-context.puml -o c4-context.png

curl -s -X POST https://kroki.io/c4plantuml/png \
  -H "Content-Type: text/plain" \
  --data-binary @c4-container.puml -o c4-container.png

echo "Rendering sequence diagrams..."
curl -s -X POST https://kroki.io/plantuml/png \
  -H "Content-Type: text/plain" \
  --data-binary @sequence-allocation.puml -o sequence-allocation.png

curl -s -X POST https://kroki.io/plantuml/png \
  -H "Content-Type: text/plain" \
  --data-binary @sequence-device-sync.puml -o sequence-device-sync.png

echo "Validating generated PNGs..."
for png in *.png; do
  size=$(stat -f%z "$png" 2>/dev/null || stat -c%s "$png" 2>/dev/null)
  if [ "$size" -lt 1000 ]; then
    echo "ERROR: $png is too small ($size bytes)"
    exit 1
  fi
  echo "  ✓ $png ($(file "$png" | cut -d: -f2))"
done

echo ""
echo "All diagrams rendered successfully!"
