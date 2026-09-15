#!/usr/bin/env bash
# Borderlands is hand-inked BLACK CONTOUR over 3D geometry plus cross-hatched
# shadow. These four are the closest named styles in the fal library; the probe
# decides which (or which stack) actually lands it.
DEST=/d/AI/comfy-models/loras
BASE=https://huggingface.co/ilkerzgi/fal-Krea-2-Style-LoRAs/resolve/main/comfy
for s in inked-comic-crosshatch bold-inked-superhero-comic graphic-novel-earthy-ink sunlit-comic-ink; do
  f="$DEST/k2_$s.safetensors"
  [ -s "$f" ] && { echo "have  $s"; continue; }
  curl -sfL -m 900 -o "$f.part" "$BASE/$s.safetensors" \
    && mv "$f.part" "$f" && echo "ok    $s" || { rm -f "$f.part"; echo "FAIL  $s"; }
done
echo DONE
