#!/bin/bash
# Scans the parent project for AI-generated images.
# Usage: ./scan_project.sh [--fix] [--report]
# Exit 0 if no ai_likely found, exit 1 if any detected (CI/pre-commit use).
cd "$(dirname "$0")" || exit 2
[ -f detector.py ] || { echo "detector.py not found"; exit 2; }
PARENT=".."
DIRS="$PARENT/public $PARENT/src/assets $PARENT/src/images $PARENT/app $PARENT/components"
FIX=""; REPORT=""
[ "$1" = "--fix" ] && FIX="--fix"
[ "$1" = "--report" ] || [ "$2" = "--report" ] && REPORT="--report"
TOTAL=0; AI=0; FIXED=0; SCANNED=0
for dir in $DIRS; do
  [ -d "$dir" ] || continue
  SCANNED=$((SCANNED + 1))
  name=$(basename "$dir")
  rep=""; [ -n "$REPORT" ] && rep="--report report_${name}.md"
  out=$(python3 detector.py "$dir" --scan $FIX $rep 2>/dev/null)
  t=$(echo "$out" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['total_images'],d['ai_likely'],d.get('fixed',0))" 2>/dev/null)
  [ -z "$t" ] && continue
  read -r ti ai fi <<< "$t"
  TOTAL=$((TOTAL + ti)); AI=$((AI + ai)); FIXED=$((FIXED + fi))
done
echo "Scanned $SCANNED directories, $TOTAL images total, $AI ai_likely, $FIXED fixed"
[ "$AI" -gt 0 ] && exit 1
exit 0
