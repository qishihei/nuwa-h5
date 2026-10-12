#!/usr/bin/env python3
# 批量抓取 25 位导演的维基百科公开肖像，存到 share/posters/portraits/<id>.jpg
# 仅作海报背景淡底用；缺图（多为在世导演无免费图）则跳过，由人工补。
import json, os, sys, urllib.request, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'directors.json')
OUT  = os.path.join(HERE, 'posters', 'portraits')
os.makedirs(OUT, exist_ok=True)

def en_title(disp):
    i = next((k for k, c in enumerate(disp) if c.isascii() and c.isalpha()), None)
    return disp[i:].strip() if i is not None else disp

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'poster-gen/1.0'})
    return urllib.request.urlopen(req, timeout=25)

data = json.load(open(DATA, encoding='utf-8'))['directors']
ok, miss = 0, []
for dr in data:
    name = dr['name']
    title = en_title(dr.get('display_name', name))
    api = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title)
    try:
        j = json.load(get(api))
        src = j.get('thumbnail', {}).get('source')
        if not src:
            raise ValueError('no thumbnail')
        raw = get(src).read()
        p = os.path.join(OUT, name + '.jpg')
        open(p, 'wb').write(raw)
        # 校验确实是张图
        Image.open(p).verify()
        ok += 1
        print('OK  ', name, '->', title)
    except Exception as e:
        miss.append((name, title, str(e)[:50]))
        print('MISS', name, '->', title, '|', e)

print(f'\n命中 {ok}/{len(data)}；缺失 {len(miss)}')
for m in miss:
    print('   补图:', m[0], '(', m[1], ') ', m[2])
