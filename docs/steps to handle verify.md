# שלב 1: בדיקת ה-Headers של ה-Patches (תאריכים ו-Commit Messages)
echo "=== Step 1: Patch Headers ==="
head -n 20 evidence_artifacts/03_2026-04-08_cell_fix_dynbind.patch
echo "--------------------------------------"
head -n 20 evidence_artifacts/04_2026-04-10_cell_rearrange_cas.patch

# שלב 2: חיפוש המילים הקריטיות בתוך ה-Patches (אימות הקשר ל-dynbind/proclaim)
echo ""
echo "=== Step 2: Critical Keywords in Patches ==="
grep -n "dynbind\|proclaim\|special\|pseudo-atomic" evidence_artifacts/03_2026-04-08_cell_fix_dynbind.patch
echo "--------------------------------------"
grep -n "dynbind\|proclaim\|special" evidence_artifacts/04_2026-04-10_cell_rearrange_cas.patch

# שלב 3: בדיקת קבצי הפלט השמורים של ה-PoC (לפני ואחרי)
echo ""
echo "=== Step 3: PoC Execution Baseline Paths ==="
cd trust_but_verify_poc
ls -l vulnerable_baseline/
ls -l patched_version/
