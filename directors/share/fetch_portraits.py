#!/usr/bin/env python3
# 批量抓取 25 位导演肖像，存到 share/posters/portraits/<id>.jpg
# 图源: IMDb suggestion 接口。下载走 curl（本机 Python urllib SSL 证书链缺失会全部失败，curl 用系统证书没问题）。
# 用法: python3 fetch_portraits.py
import json, os, subprocess, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, 'posters', 'portraits')
os.makedirs(OUT, exist_ok=True)

# 导演 id -> IMDb 检索名（显式映射，避免同名人混淆）
IMDB_NAMES = {
    'akira-kurosawa': 'Akira Kurosawa',
    'alfred-hitchcock': 'Alfred Hitchcock',
    'andrei-tarkovsky': 'Andrei Tarkovsky',
    'ang-lee': 'Ang Lee',
    'abbas-kiarostami': 'Abbas Kiarostami',
    'bong-joon-ho': 'Bong Joon Ho',
    'charlie-chaplin': 'Charlie Chaplin',
    'christopher-nolan': 'Christopher Nolan',
    'david-lynch': 'David Lynch',
    'edward-yang': 'Edward Yang',
    'federico-fellini': 'Federico Fellini',
    'francis-coppola': 'Francis Ford Coppola',
    'hayao-miyazaki': 'Hayao Miyazaki',
    'hou-hsiao-hsien': 'Hou Hsiao-hsien',
    'ingmar-bergman': 'Ingmar Bergman',
    'jean-luc-godard': 'Jean-Luc Godard',
    'jean-renoir': 'Jean Renoir',
    'krzysztof-kieslowski': 'Krzysztof Kieslowski',
    'martin-scorsese': 'Martin Scorsese',
    'michelangelo-antonioni': 'Michelangelo Antonioni',
    'orson-welles': 'Orson Welles',
    'stanley-kubrick': 'Stanley Kubrick',
    'takeshi-kitano': 'Takeshi Kitano',
    'wong-kar-wai': 'Wong Kar-wai',
    'yasujiro-ozu': 'Yasujiro Ozu',
}

def curl_bytes(url, timeout=30):
    r = subprocess.run(['curl', '-s', '-m', str(timeout), '-A', 'Mozilla/5.0', url],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f'curl exit {r.returncode}')
    return r.stdout

def imdb_image_url(query):
    letter = query[0].lower()
    api = f'https://v2.sg.media-imdb.com/suggestion/{letter}/{urllib.parse.quote(query)}.json'
    j = json.loads(curl_bytes(api))
    items = j.get('d', [])
    # 优先取「人物条目」（id 以 nm 开头），避免拿到影视海报/专题图
    items.sort(key=lambda x: 0 if str(x.get('id', '')).startswith('nm') else 1)
    for item in items:
        img = item.get('i', {}).get('imageUrl')
        if img:
            # 缩到宽 480，够海报用且省流量
            return img.replace('._V1_.jpg', '._V1_QL75_UX480_.jpg'), item.get('l', '')
    return None, None

ok, miss = 0, []
for did, q in IMDB_NAMES.items():
    dest = os.path.join(OUT, did + '.jpg')
    try:
        src, hit = imdb_image_url(q)
        if not src:
            raise ValueError('no image in suggestion')
        open(dest, 'wb').write(curl_bytes(src))
        im = Image.open(dest); im.verify()
        im = Image.open(dest)              # 二次打开确认无损坏
        ok += 1
        print(f'OK   {did:24s} <- {q} (IMDb命中: {hit}, {im.size[0]}x{im.size[1]})')
    except Exception as e:
        miss.append((did, q, str(e)[:60]))
        print(f'MISS {did:24s} <- {q} | {e}')

print(f'\n命中 {ok}/{len(IMDB_NAMES)}；缺失 {len(miss)}')
for m in miss:
    print('   需人工补图:', m[0], '(', m[1], ') ', m[2])
