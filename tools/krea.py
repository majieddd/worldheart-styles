"""Krea 2 Turbo renderer over the ComfyUI HTTP API.

Graph is the official ComfyUI template `image_krea2_turbo_t2i` with the
prompt-enhancement LLM stripped out: we write our own prompts, and an LLM
rewriting them mid-flight would break the catalogue contract (the prompt on
file must be the prompt the model saw).

    UNETLoader -> [LoraLoaderModelOnly]* -> KSampler -> VAEDecode -> SaveImage
    CLIPLoader -> CLIPTextEncode -> positive, and ConditioningZeroOut -> negative
    EmptyLatentImage -> KSampler latent

Turbo is distilled for 8 steps with guidance disabled, so cfg is 1.0 and there
is no real negative branch -- ConditioningZeroOut is what the template uses and
what the distillation expects.
"""
import hashlib, json, os, time, urllib.request, urllib.error

SERVER = os.environ.get('COMFY', '127.0.0.1:8188')
UNET   = 'krea2_turbo_fp8_scaled.safetensors'
CLIP   = 'qwen3vl_4b_fp8_scaled.safetensors'
VAE    = 'qwen_image_vae.safetensors'
STEPS, CFG, SAMPLER, SCHED = 8, 1.0, 'euler', 'simple'


def seed_of(key):
    """FNV-1a over the key: stable across runs and processes.

    Python salts str.__hash__ per process, so the builtin would re-roll every
    key on a resumed run. A key must render the same image every time or a
    re-render stops being a restore and becomes a re-roll.
    """
    h = 2166136261
    for ch in key:
        h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
    return h % (2 ** 31)


def graph(prompt, w, h, seed, loras=(), prefix='wh'):
    g = {
        '10': {'class_type': 'UNETLoader',
               'inputs': {'unet_name': UNET, 'weight_dtype': 'default'}},
        '11': {'class_type': 'CLIPLoader',
               'inputs': {'clip_name': CLIP, 'type': 'krea2', 'device': 'default'}},
        '12': {'class_type': 'VAELoader', 'inputs': {'vae_name': VAE}},
        '6':  {'class_type': 'CLIPTextEncode',
               'inputs': {'clip': ['11', 0], 'text': prompt}},
        '13': {'class_type': 'ConditioningZeroOut', 'inputs': {'conditioning': ['6', 0]}},
        '5':  {'class_type': 'EmptyLatentImage',
               'inputs': {'width': w, 'height': h, 'batch_size': 1}},
        '3':  {'class_type': 'KSampler',
               'inputs': {'model': ['10', 0], 'positive': ['6', 0], 'negative': ['13', 0],
                          'latent_image': ['5', 0], 'seed': seed, 'steps': STEPS,
                          'cfg': CFG, 'sampler_name': SAMPLER, 'scheduler': SCHED,
                          'denoise': 1.0}},
        '8':  {'class_type': 'VAEDecode', 'inputs': {'samples': ['3', 0], 'vae': ['12', 0]}},
        '29': {'class_type': 'SaveImage',
               'inputs': {'images': ['8', 0], 'filename_prefix': prefix}},
    }
    # LoRAs chain model-only: the Qwen3-VL text encoder is shared and patching
    # it per-LoRA would force a re-encode of every prompt for every stack.
    src = ['10', 0]
    for i, (name, strength) in enumerate(loras):
        nid = str(100 + i)
        g[nid] = {'class_type': 'LoraLoaderModelOnly',
                  'inputs': {'model': src, 'lora_name': name, 'strength_model': strength}}
        src = [nid, 0]
    g['3']['inputs']['model'] = src
    return g


def _post(path, payload):
    req = urllib.request.Request('http://%s%s' % (SERVER, path),
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))


def _get(path):
    return json.load(urllib.request.urlopen('http://%s%s' % (SERVER, path), timeout=60))


def render(prompt, w, h, seed, loras=(), prefix='wh', timeout=900):
    pid = _post('/prompt', {'prompt': graph(prompt, w, h, seed, loras, prefix)})['prompt_id']
    t0 = time.time()
    while time.time() - t0 < timeout:
        hist = _get('/history/' + pid)
        if pid in hist:
            h_ = hist[pid]
            st = h_.get('status', {})
            if st.get('status_str') == 'error' or not st.get('completed', True):
                raise RuntimeError('comfy error: ' + json.dumps(st)[:900])
            for out in h_.get('outputs', {}).values():
                for im in out.get('images', []):
                    return im, time.time() - t0
            raise RuntimeError('completed with no image: ' + json.dumps(h_)[:500])
        time.sleep(0.4)
    raise TimeoutError('render exceeded %ss' % timeout)


def fetch(im):
    q = urllib.parse.urlencode({'filename': im['filename'], 'subfolder': im.get('subfolder', ''),
                                'type': im.get('type', 'output')})
    return urllib.request.urlopen('http://%s/view?%s' % (SERVER, q), timeout=120).read()


import urllib.parse  # noqa: E402  (used by fetch)
