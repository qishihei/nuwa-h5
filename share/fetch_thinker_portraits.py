#!/usr/bin/env python3
# 批量抓取 25 位思想家肖像，存到 share/posters/portraits/<id>.jpg
# 图源: IMDb suggestion 接口（现代人物）+ 维基百科 REST summary（古代思想家，画作/雕像）
# 下载走 curl（本机 Python urllib SSL 证书链缺失会全部失败，curl 用系统证书没问题）。
# 用法: python3 fetch_thinker_portraits.py
import json, os, re, subprocess, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, 'posters', 'portraits')
os.makedirs(OUT, exist_ok=True)

# id -> (IMDb 检索名或 None, 维基 (中/英标题))
THINKERS = {
    'charlie-munger':       ('Charlie Munger',        ('查理·芒格', 'Charlie Munger')),
    'elon-musk':            ('Elon Musk',             ('埃隆·马斯克', 'Elon Musk')),
    'richard-feynman':      ('Richard Feynman',       ('理查德·费曼', 'Richard Feynman')),
    'zhang-yiming':         (None,                    ('张一鸣', 'Zhang Yiming')),
    'naval-ravikant':       ('Naval Ravikant',        (None, 'Naval Ravikant')),
    'steve-jobs':           ('Steve Jobs',            ('史蒂夫·乔布斯', 'Steve Jobs')),
    'kazuo-inamori':        ('Kazuo Inamori',         ('稻盛和夫', 'Kazuo Inamori')),
    'wang-yangming':        (None,                    ('王守仁', 'Wang Yangming')),
    'socrates':             (None,                    ('苏格拉底', 'Socrates')),
    'warren-buffett':       ('Warren Buffett',        ('沃伦·巴菲特', 'Warren Buffett')),
    'ray-dalio':            ('Ray Dalio',             (None, 'Ray Dalio')),
    'confucius':            (None,                    ('孔子', 'Confucius')),
    'friedrich-nietzsche':  ('Friedrich Nietzsche',   ('弗里德里希·尼采', 'Friedrich Nietzsche')),
    'laozi':                (None,                    ('老子', 'Laozi')),
    'marie-curie':          ('Marie Curie',           ('玛丽·居里', 'Marie Curie')),
    'daniel-kahneman':      ('Daniel Kahneman',       ('丹尼尔·卡尼曼', 'Daniel Kahneman')),
    'sun-tzu':              (None,                    ('孫武', 'Sun Tzu')),
    'jensen-huang':         ('Jensen Huang',          ('黄仁勋', 'Jensen Huang')),
    'coco-chanel':          ('Coco Chanel',           ('可可·香奈儿', 'Coco Chanel')),
    'nassim-taleb':         ('Nassim Nicholas Taleb', (None, 'Nassim Nicholas Taleb')),
    'sima-qian':            (None,                    ('司马迁', 'Sima Qian')),
    'sam-altman':           ('Sam Altman',            ('山姆·奥尔特曼', 'Sam Altman')),
    'liqingzhao':           (None,                    ('李清照', 'Li Qingzhao')),
    'friedrich-hayek':      ('Friedrich Hayek',       ('弗里德里希·哈耶克', 'Friedrich Hayek')),
    'john-maynard-keynes':  ('John Maynard Keynes',   ('约翰·梅纳德·凯恩斯', 'John Maynard Keynes')),
}

def curl_bytes(url, timeout=30):
    r = subprocess.run(['curl', '-s', '-m', str(timeout), '-A', 'Mozilla/5.0 (Macintosh)', url],
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
    # 人名校验：查询词的每个实词都要出现在命中名里，防止抓到同名演员（如 Ray Dalio -> Stevie Ray Dallimore）
    toks = [t for t in re.split(r'\s+', query.lower()) if len(t) >= 3]
    for item in items:
        name = str(item.get('l', '')).lower()
        if toks and not all(t in name for t in toks):
            continue
        img = item.get('i', {}).get('imageUrl')
        if img:
            return img.replace('._V1_.jpg', '._V1_QL75_UX480_.jpg'), item.get('l', '')
    return None, None

# 360 图片搜索兜底（维基本机网络不通；古代思想家用画像/雕像）
SO360_QUERIES = {
    'zhang-yiming':    '张一鸣 字节跳动 照片',
    'naval-ravikant':  '纳瓦尔 拉维坎特 Naval Ravikant',
    'kazuo-inamori':   '稻盛和夫 照片',
    'daniel-kahneman': '丹尼尔·卡尼曼 心理学家 照片',
    'nassim-taleb':    'Nassim Taleb 照片',
    'confucius':       '孔子 画像',
    'laozi':           '老子 画像',
    'sun-tzu':         '孙武 画像',
    'wang-yangming':   '王阳明 画像',
    'socrates':        '苏格拉底 雕像',
    'sima-qian':       '司马迁 画像',
    'liqingzhao':      '李清照 画像',
    'ray-dalio':       '瑞·达利欧 桥水基金',
}

def so360_image_urls(query, min_w=300):
    """360 图片搜索，返回候选 url 列表（按圆形裁剪友好度排序）"""
    api = 'https://image.so.com/j?q=%s&src=srp&pn=30&sn=0' % urllib.parse.quote(query)
    j = None
    for attempt in range(4):            # 接口间歇性限流，重试
        raw = curl_bytes(api)
        try:
            j = json.loads(raw)
            break
        except Exception:
            import time; time.sleep(8)
    if not j:
        return []
    cands = []
    for it in j.get('list', []):
        img = it.get('img') or it.get('downurl_true')
        if not img:
            continue
        try:
            w, h = int(it.get('width') or 0), int(it.get('height') or 0)
        except ValueError:
            w = h = 0
        if w and w < min_w:
            continue
        if h and w and w / h > 2.2:
            continue  # 排除横幅/长图
        # 优先接近方形/竖版的（圆形裁剪友好），按宽高比偏差排序
        cands.append((abs((w or 600) / (h or 800) - 0.75), img))
    cands.sort()
    return [c[1] for c in cands]

def wiki_image_url(titles):
    """维基 REST summary：zh 优先，失败回落 en。返回 (图片url, 来源描述)"""
    for lang, title in [titles]:
        if not title:
            continue
        try:
            api = f'https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}'
            j = json.loads(curl_bytes(api))
            oi = j.get('originalimage') or {}
            th = j.get('thumbnail') or {}
            if oi.get('source') and 200 <= oi.get('width', 0) <= 6000:
                return oi['source'], f'{lang}wiki:{title}'
            if th.get('source'):
                # 缩略图放大到 600px（维基 thumb URL 内嵌尺寸）
                src = re.sub(r'/(\d+)px-', '/600px-', th['source'])
                return src, f'{lang}wiki:{title}'
        except Exception:
            continue
    return None, None

ok, miss = 0, []
for tid, (imdb_q, wiki_titles) in THINKERS.items():
    dest = os.path.join(OUT, tid + '.jpg')
    if os.path.exists(dest):
        try:
            Image.open(dest).verify(); ok += 1
            print(f'SKIP {tid:22s} 已存在')
            continue
        except Exception:
            os.remove(dest)
    src, hit = None, None
    cands = []                            # (来源描述, url) 列表，逐个尝试下载
    try:
        if imdb_q:
            src, hit = imdb_image_url(imdb_q)
            if src: cands.append((hit, src))
    except Exception as e:
        hit = f'IMDb失败({e})'
    q360 = SO360_QUERIES.get(tid)
    if q360:
        try:
            for u in so360_image_urls(q360):
                cands.append((f'360:{q360}', u))
        except Exception as e:
            print(f'WARN {tid:22s} | 360检索失败 {e}')
    try:
        wsrc, whit = wiki_image_url(wiki_titles)
        if wsrc: cands.append((whit, wsrc))
    except Exception:
        pass
    saved = False
    for hdesc, u in cands:
        try:
            open(dest, 'wb').write(curl_bytes(u))
            im = Image.open(dest); im.verify()
            im = Image.open(dest)
            if im.size[0] < 200:
                raise ValueError(f'过小 {im.size[0]}x{im.size[1]}')
            ok += 1; saved = True
            print(f'OK   {tid:22s} <- {hdesc} ({im.size[0]}x{im.size[1]})')
            break
        except Exception as e:
            if os.path.exists(dest): os.remove(dest)
            last_err = str(e)[:60]
            print(f'...  {tid:22s} | 候选失败({hdesc}) {last_err}，试下一个')
    if not saved:
        miss.append((tid, imdb_q or '', str(hit)))
        print(f'MISS {tid:22s} | {hit}')

print(f'\n命中 {ok}/{len(THINKERS)}；缺失 {len(miss)}')
for m in miss:
    print('   需人工补图:', m[0], '(', m[1], ') ', m[2])
