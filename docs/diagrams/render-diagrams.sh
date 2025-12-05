#!/bin/bash
# Render all PlantUML diagrams using Kroki
# Usage: ./render-diagrams.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Rendering C4 diagrams (c4plantuml) ==="
for puml in c4-*.puml; do
    png="${puml%.puml}.png"
    echo "  Rendering $puml -> $png"
    curl -s -X POST https://kroki.io/c4plantuml/png \
        -H "Content-Type: text/plain" \
        --data-binary @"$puml" -o "$png"
done

echo ""
echo "=== Rendering sequence diagrams (plantuml) ==="
for puml in sequence-*.puml; do
    png="${puml%.puml}.png"
    echo "  Rendering $puml -> $png"
    curl -s -X POST https://kroki.io/plantuml/png \
        -H "Content-Type: text/plain" \
        --data-binary @"$puml" -o "$png"
done

echo ""
echo "=== Validating generated PNGs ==="
for png in *.png; do
    size=$(stat -f%z "$png" 2>/dev/null || stat -c%s "$png" 2>/dev/null)
    if [ "$size" -lt 1000 ]; then
        echo "  ERROR: $png is too small ($size bytes)"
        exit 1
    fi
    info=$(file "$png" | cut -d: -f2 | xargs)
    echo "  ✓ $png ($info)"
done

echo ""
echo "=== All diagrams rendered successfully! ==="
