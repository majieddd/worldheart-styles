#!/usr/bin/env bash
# Probe set: one LoRA per stylistic axis this brief could plausibly take.
# Everything from ilkerzgi/fal-Krea-2-Style-LoRAs comes from its comfy/ folder,
# which is already in ComfyUI key layout; the diffusers-named siblings need a
# remap and there is no reason to pay for one.
DEST=/d/AI/comfy-models/loras
mkdir -p "$DEST"
BASE=https://huggingface.co/ilkerzgi/fal-Krea-2-Style-LoRAs/resolve/main/comfy
STYLES="terracotta-lowpoly-miniature bold-clay-toy-render miniature-diorama-figurine
vivid-cel-shaded-anime bold-inked-anime-realism misty-anime-cinematic
sunlit-painterly-anime misty-dark-fantasy-render amber-lit-fantasy-filmset
early-cgi-surreal-render moody-desaturated-film-grain warm-faceted-cartoon
retro-anime-cel-render chrome-iridescent-render vintage-plastic-toy
glowing-ember-fantasy"
for s in $STYLES; do
  f="$DEST/k2_$s.safetensors"
  [ -s "$f" ] && { echo "have  $s"; continue; }
  curl -sfL -m 900 -o "$f.part" "$BASE/$s.safetensors" \
    && mv "$f.part" "$f" && echo "ok    $s" || { rm -f "$f.part"; echo "FAIL  $s"; }
done
# Two standalone repos worth having: the official Krea retro-anime LoRA, and a
# realism LoRA to buy back the grounding grit the anime styles spend.
curl -sfL -m 900 -o "$DEST/k2_official_retroanime.safetensors" \
  "https://huggingface.co/krea/Krea-2-LoRA-retroanime/resolve/main/retroanime.safetensors" \
  && echo "ok    official-retroanime" || echo "FAIL  official-retroanime"
curl -sfL -m 900 -o "$DEST/k2_realism.safetensors" \
  "https://huggingface.co/gokaygokay/Krea-2-Realism-LoRA/resolve/main/krea2_realism_lora.safetensors" \
  && echo "ok    realism" || echo "FAIL  realism"
echo "DONE"; ls -la "$DEST" | tail -25
