#!/usr/bin/env bash
# Re-stage and publish the GitHub Pages site.
#
# _pages/ is a throwaway assembly of the referenced files only, but it keeps its
# own .git so history survives a re-stage: stage_pages.py rebuilds the working
# tree, git sees the diff, and unchanged files (the 164 plates, the meshes)
# are not re-uploaded.
set -euo pipefail
cd "$(dirname "$0")/.."

# Regenerate the boards first, so a catalogue or prompt edit is picked up.
python tools/build_gallery.py
python tools/build_styles_page.py
cp styles.html index.html

# stage_pages.py exits non-zero if any page references a file that did not
# ship, which is the one failure the site cannot show you itself.
python tools/stage_pages.py

cd _pages
git add -A
if git diff --cached --quiet; then
  echo "nothing changed"; exit 0
fi
git commit -q -m "${1:-Update WorldHeart boards}

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push -q origin main
echo "pushed — https://majieddd.github.io/worldheart-styles/ rebuilds in ~1 min"
