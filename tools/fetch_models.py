# -*- coding: utf-8 -*-
"""Pull the nine Higgsfield GLBs into models3d/.

Re-runnable and idempotent: a file already on disk is skipped, so this doubles
as the recovery path if the working tree is moved or a model is deleted. The
URLs are Higgsfield CDN paths recorded at generation time and kept in
hf/manifest.json alongside their job ids.
"""
import json, os, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'models3d')
B = "https://d8j0ntlcm91z4.cloudfront.net/user_3IW1qpG7eVV30fIBOq2oLvLODjC/"

FILES = {
 'retroanime_commander': 'hf_20260915_183947_84da6677-02d4-431a-8a8b-126f13ffa5fd.glb',
 'retroanime_enemy':     'hf_20260915_184056_bc533145-2871-488e-b220-7af7ddf2f59e.glb',
 'retroanime_tower':     'hf_20260915_184058_1357d51c-0578-4e49-933c-d3d29338625b.glb',
 'inkcel_commander':     'hf_20260915_184101_b0ff2587-80ee-4a24-ad02-d7226f4b0eb6.glb',
 'inkcel_enemy':         'hf_20260915_184102_d3725b05-e1e4-4ed6-9276-6b2d5411a5f9.glb',
 'inkcel_tower':         'hf_20260915_184106_9c54ec0c-8bf7-482e-9b13-ea2e88c64273.glb',
 'inkline_commander':    'hf_20260915_184107_33926a5a-a6a3-40a9-975d-757ff26082a3.glb',
 'inkline_enemy':        'hf_20260915_184109_915d3acc-1582-45dc-8ddd-1bb106cdda04.glb',
 'inkline_tower':        'hf_20260915_184110_85fee003-5c61-4803-af95-70759f8b50ab.glb',
}


def main():
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(HERE, 'hf', 'manifest.json')
    man = json.load(open(mpath, encoding='utf-8')) if os.path.exists(mpath) else {}
    man.setdefault('model_urls', {})
    total = 0
    for name, fn in FILES.items():
        dst = os.path.join(OUT, name + '.glb')
        man['model_urls'][name] = B + fn
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            print('%-22s have  %6.1f MB' % (name, os.path.getsize(dst) / 1048576))
            total += os.path.getsize(dst)
            continue
        urllib.request.urlretrieve(B + fn, dst)
        sz = os.path.getsize(dst)
        total += sz
        print('%-22s ok    %6.1f MB' % (name, sz / 1048576))
    if os.path.exists(os.path.dirname(mpath)):
        json.dump(man, open(mpath, 'w'), indent=1)
    print('total %.1f MB across %d models' % (total / 1048576, len(FILES)))


if __name__ == '__main__':
    main()
