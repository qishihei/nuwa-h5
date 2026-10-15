#!/usr/bin/env python3
# 生成「导演沙龙」爆款引流知识卡片（杂志排版风：大标题+照片+双栏+反套路观点+金句+二维码）
# 用法: python3 make_flow_cards.py [访问地址] [check]
#   check = 仅生成裁切拼图 cards/_check.png 供目检，不生成正式卡片
# 产物: directors/share/cards/<director-id>.png (25 张) + index.html (预览画廊)
# 肖像: directors/share/posters/portraits/<id>.jpg

import os, sys, json, hashlib
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

BASE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ('check',) else 'https://director-salon.onrender.com'
CHECK = 'check' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
PORTRAITS = os.path.join(HERE, 'posters', 'portraits')
OUT = os.path.join(HERE, 'cards')
os.makedirs(OUT, exist_ok=True)

CJK = '/System/Library/Fonts/PingFang.ttc'
W = 1080
INK = (17, 17, 17, 255)
GRAY = (90, 88, 84, 255)
DIM = (130, 126, 120, 255)
PAPER = (247, 245, 242, 255)
BOX = (233, 231, 227, 255)
LABEL_CONTRA = '反套路视角：'

def probe_font():
    # 注意：本机 PIL + PingFang.ttc 对"迈/远"等字会渲染成空白（缺字 bug），
    # 统一改用 Hiragino Sans GB：W6(粗)做标题、W3(常规)做正文
    hira = '/System/Library/Fonts/Hiragino Sans GB.ttc'
    try:
        ImageFont.truetype(hira, 40, index=2)
        return (hira, 2), (hira, 0)
    except Exception:
        pass
    heavy = regular = None
    for idx in range(10):
        try:
            f = ImageFont.truetype(CJK, 40, index=idx)
            name = ' '.join(f.getname())
            if 'Semibold' in name and heavy is None: heavy = (CJK, idx)
            if 'Regular' in name and regular is None: regular = (CJK, idx)
        except Exception:
            break
    if heavy is None: heavy = regular
    if regular is None: regular = (CJK, 0)
    return heavy, regular

HEAVY, REGULAR = probe_font()

def font(spec, size):
    path, idx = (spec if isinstance(spec, tuple) else (spec, 0))
    try: return ImageFont.truetype(path, size, index=idx)
    except Exception: return ImageFont.load_default()

def fit_font(text, spec, start, min_size, max_width, spacing=0):
    size = start
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    while size > min_size:
        f = font(spec, size)
        w = sum(d.textlength(ch, font=f) for ch in text) + spacing * max(0, len(text) - 1)
        if w <= max_width: return f, size
        size -= 2
    return font(spec, min_size), min_size

def wrap(text, fnt, max_w):
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    lines, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=fnt) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines

CROP_Y = {
    'stanley-kubrick': 0.18,
    'christopher-nolan': 0.20,
    'wong-kar-wai': 0.44,
    'charlie-chaplin': 0.45,
    'federico-fellini': 0.45,
    'michelangelo-antonioni': 0.50,
    'hou-hsiao-hsien': 0.50,
    'ang-lee': 0.50,
    'david-lynch': 0.50,
    'orson-welles': 0.35,
    'abbas-kiarostami': 0.35,
    'yasujiro-ozu': 0.30,
}

def smart_centering(img, tw, th, tid):
    W0, H0 = img.size
    if tid in CROP_Y:
        return (0.5, CROP_Y[tid])
    ch = W0 * th / tw
    if ch >= H0:
        return (0.5, 0.5)
    g = img.convert('L').resize((60, 60))
    e = g.filter(ImageFilter.FIND_EDGES)
    px = e.load()
    rows = [sum(px[x, y] for x in range(60)) for y in range(60)]
    win = max(2, round(60 * ch / H0))
    best, best_top = -1, 0
    for top in range(0, 60 - win + 1):
        s = sum(rows[top:top + win]) * (1 + 0.35 * (1 - top / 60))
        if s > best: best, best_top = s, top
    cy = (best_top / 60) / max(1e-6, 1 - ch / H0)
    return (0.5, min(max(cy, 0.0), 1.0))

def qr_png(url, size=300):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color='#111111', back_color='white').convert('RGBA')
    return img.resize((size, size))

def cn_name(disp):
    import re
    return re.split(r'(?=[A-Za-z])', disp or '')[0].strip() or disp

# ---------- 每位导演的卡片文案 ----------
CARDS = {
 'akira-kurosawa': dict(
   h=['把人逼到绝境，', '人性自己会显形'],
   remind='提醒：真正的张力不在打斗，而在两难。',
   left=['七武士里没有英雄，', '只有被时代碾过', '却不肯倒下的普通人。', '让天地比人更大，', '渺小与尊严同时成立。'],
   right=['他退后摄影机，', '把人放进风雨泥泞里，', '一刀一雨，', '胜过千句台词说教。'],
   contra='所谓大师手笔，不过是把最简单的冲突拍到极致。',
   bottom=['把人逼到墙角，', '故事自己会说话。']),
 'alfred-hitchcock': dict(
   h=['悬念不是 surprise，', '是观众更早知道'],
   remind='提醒：让人坐立难安的，是"知道要发生"却"无可奈何"。',
   left=['他从不藏凶手，', '偏把炸弹提前亮给观众，', '让等待本身成为折磨。', '这就是悬念——', '不是谜底，是煎熬。'],
   right=['麦格芬是无物，', '却驱动所有人疯跑。', '观众追的从不是那东西，', '是自己的恐惧。'],
   contra='好看的故事不在反转多少，在你敢不敢让观众先知道。',
   bottom=['最稳的椅子，', '是坐在炸弹上。']),
 'andrei-tarkovsky': dict(
   h=['时间，', '才是真正的演员'],
   remind='提醒：他拍的不是事件，是时间如何在脸上流淌。',
   left=['别人用剪辑偷时间，', '他让镜头停着，', '等雨落下、等火燃尽、', '等一个人慢慢变老。'],
   right=['长镜头不是炫技，', '是把观众钉进真实里，', '逼你与无聊、', '与神圣共处。'],
   contra='节奏快从不等于有内容，慢下来才可能看见。',
   bottom=['雕刻时光，', '而非切割它。']),
 'ang-lee': dict(
   h=['克制，', '是最难的演技'],
   remind='提醒：情绪不必喊出来，收得住的才进得去心。',
   left=['断背山的爱，', '他不让角色说破，', '一个眼神、一次背影，', '比告白重十倍。'],
   right=['他游走东西之间，', '不站队，只求真：', '武侠要讲礼，', '家庭要讲忍。'],
   contra='技术再满，抵不过一个"准"字——精确比华丽更难。',
   bottom=['收着的情感，', '回头才砸下来。']),
 'bong-joon-ho': dict(
   h=['类型只是壳，', '阶级才是肉'],
   remind='提醒：把富人穷人塞进同一部电影，荒诞就自己长出来。',
   left=['寄生虫里半地下室的人，', '一遍遍按灭灯泡，', '光是免费的，', '却照不进他们的生活。'],
   right=['他混搭喜剧惊悚，', '让观众笑着笑着眼眶就红了——', '类型是用来骗你', '掉进现实陷阱的。'],
   contra='让人发笑再让人心碎，比单纯催泪更残忍。',
   bottom=['同一场雨，', '有人淋湿有人遮伞。']),
 'charlie-chaplin': dict(
   h=['笑着笑着，', '你就哭了'],
   remind='提醒：默片里没有声音，却比任何台词都吵。',
   left=['一个捡煤渣的小人物，', '把帽子当宝贝、把尊严当命，', '摔得越狠，', '越显出人的体面。'],
   right=['他让全世界看懂：', '穷人的幽默，', '是对命运最体面', '的反击。'],
   contra='喜剧的尽头不是笑，是被看见的孤独。',
   bottom=['小人物一迈腿，', '全世界都跟着走。']),
 'christopher-nolan': dict(
   h=['时间，', '是他唯一的反派'],
   remind='提醒：结构即叙事——怎么讲，和讲什么一样重要。',
   left=['他偏用胶片实拍 rotations，', '把太空、梦境、战争', '拆成一块块钟表，', '让观众自己拼。'],
   right=['不靠特效堆奇观，', '靠逻辑逼你思考：', '你以为在看故事，', '其实在被重新训练时间感。'],
   contra='烧脑不是炫技，是放手让你参与建构。',
   bottom=['别信时间，', '它最会骗人。']),
 'david-lynch': dict(
   h=['表面越平静，', '底下越黑暗'],
   remind='提醒：美国小镇的蓝天，往往是噩梦的封面。',
   left=['他从不解释谜，', '只把红帘、黑咖啡、', '电流杂音扔给你，', '让你自己发毛。'],
   right=['理性分析会毁掉他的电影，', '要用直觉、用梦去接——', '潜意识才是', '真正的放映厅。'],
   contra='看懂不是目的，被触动才是。',
   bottom=['别追答案，', '去听那片杂音。']),
 'edward-yang': dict(
   h=['城市很大，', '人很孤独'],
   remind='提醒：他用冷静的镜头解剖中产，刀口不见血。',
   left=['一一里那场婚礼，', '满屏人脸，', '每个人都在笑，', '每个人都被困在自己的格子。'],
   right=['他不信煽情，', '把社会矛盾摊开给你看，', '留白处，', '全是没说出口的崩塌。'],
   contra='最锋利的社会批判，往往最不动声色。',
   bottom=['热闹是他们的，', '崩溃也是。']),
 'federico-fellini': dict(
   h=['记忆一搅拌，', '现实就醉了'],
   remind='提醒：他拍的不是故事，是脑子里那场永不散场的马戏。',
   left=['小丑、肥女、神父、', '儿时的海浪——', '统统混进一场梦境游行，', '真实与幻想握手言和。'],
   right=['他说电影该像梦，', '不必讲理，', '只要真诚地荒谬，', '观众就会认出自己的夜。'],
   contra='循规蹈矩的"真实"，常常比梦境更假。',
   bottom=['人生如马戏，', '散场也别醒。']),
 'francis-coppola': dict(
   h=['野心一膨胀，', '人就失控'],
   remind='提醒：他拍权力如何腐蚀，也亲历野心如何反噬自己。',
   left=['现代启示录里，', '文明退潮，', '人退回最原始的', '恐惧与神性。'],
   right=['他押上全部身家拍片，', '片场如战场——', '创作与疯狂', '只有一线之隔。'],
   contra='最危险的作品，往往诞生于创作者也失控的边缘。',
   bottom=['爱上权力，', '就被它带走。']),
 'hayao-miyazaki': dict(
   h=['会飞的人，', '最懂大地'],
   remind='提醒：他给童年插上翅膀，却从不避谈死亡与战争。',
   left=['天空之城不是逃避，', '是另一种认真：', '飞翔是为了', '更看清脚下的土地。'],
   right=['他的童真有重量，', '炸弹会炸、人会死，', '正因如此，', '温柔才格外珍贵。'],
   contra='给孩子的故事，不必删去世界的残酷。',
   bottom=['飞得越高，', '越要记得回来。']),
 'hou-hsiao-hsien': dict(
   h=['不动声色，', '时代自己走过'],
   remind='提醒：他不爱解释，把镜头搁远，让历史自己发生。',
   left=['悲情城市里，', '镜头静静停在巷口，', '人物的命运', '在烟火气里悄悄改写。'],
   right=['留白不是空，', '是把想象留给观众——', '你看到的沉默，', '比台词更响。'],
   contra='克制不是冷淡，是把情绪埋进时间的厚度。',
   bottom=['时代不说话，', '但它从未缺席。']),
 'ingmar-bergman': dict(
   h=['信仰缺席处，', '人只剩对话'],
   remind='提醒：他把上帝请下神坛，只留下人与人的正面交锋。',
   left=['第七封印里，', '骑士和死神下棋，', '不是怕死，', '是怕这辈子没活明白。'],
   right=['他用特写逼问：', '爱、罪、沉默——', '没有答案，', '但问本身已是救赎。'],
   contra='真正的精神拷问，往往发生在两个人面对面的时候。',
   bottom=['沉默里，', '住着最响的疑问。']),
 'jean-luc-godard': dict(
   h=['规则是用来', '被剪断的'],
   remind='提醒：他拿跳切当武器，把电影语法砸碎重来。',
   left=['不被叙事绑架，', '字幕可以吵架、', '镜头可以叛逃，', '电影从此有了', '自己的脾气。'],
   right=['他说政治即电影，', '把标语、股票、情书', '剪进同一帧——', '混乱里藏着清醒。'],
   contra='颠覆形式，本身就是在表达立场。',
   bottom=['不破，', '怎么立。']),
 'jean-renoir': dict(
   h=['宽容，', '是唯一的胜利'],
   remind='提醒：他镜头下没有绝对坏人，只有各自处境。',
   left=['游戏规则里，', '上流社会的体面', '是一层薄冰，', '底下全是算计与脆弱。'],
   right=['他让人谅解而非审判，', '因为每个人', '都被自己的时代', '绑着走。'],
   contra='恨一个人很容易，理解他才需要本事。',
   bottom=['人人都有苦衷，', '宽容才是体面。']),
 'krzysztof-kieslowski': dict(
   h=['一个偶然，', '改写整个人生'],
   remind='提醒：他迷恋命运的岔路——你选的与撞上的，谁更决定一切？',
   left=['红白蓝里，', '一个电话拨错、', '一件外套拾起，', '素不相识的人', '被命运缝在一起。'],
   right=['他不信宏大叙事，', '只在道德两难里', '轻轻一推——', '你就回不了头。'],
   contra='最重的抉择，常常披着最轻的偶然。',
   bottom=['命运爱开玩笑，', '你我都是梗。']),
 'martin-scorsese': dict(
   h=['罪与疚，', '是男人一生的回旋镖'],
   remind='提醒：他拍的从来不是黑帮，是良知如何被自己缠死。',
   left=['好家伙里，', '一夜暴富、一夜背叛，', '钱来得快，', '债也来得准。'],
   right=['他用镜头高烧、', '用音乐布道，', '让观众和角色一起', '沉进无法赦免的夜。'],
   contra='最狠的审判不在法庭，在凌晨三点醒来的自己。',
   bottom=['逃得掉仇家，', '逃不掉自己。']),
 'michelangelo-antonioni': dict(
   h=['东西再多，', '人越空'],
   remind='提醒：他拍现代性的空虚——拥有了一切，却说不出要什么。',
   left=['红色沙漠里，', '工业灰雾吞掉颜色，', '人也失了轮廓，', '连情绪都找不到名字。'],
   right=['他不给答案，', '只把疏离铺成风景，', '让你在空镜里', '照见自己的静默。'],
   contra='物质填满房间，却掏空了人，这才是现代病。',
   bottom=['拥有很多，', '却说不清要什么。']),
 'orson-welles': dict(
   h=['景深里，', '藏着权力的谎言'],
   remind='提醒：他让画面前后都清晰，逼你同时看真相与表演。',
   left=['公民凯恩里，', '"玫瑰花蕾"追了一生，', '到头来，', '不过是个雪橇的名字。'],
   right=['他用叙述者互相拆台，', '告诉你：', '没有人能还原一个人，', '连他自己也不能。'],
   contra='最完整的传记，往往是最精巧的骗局。',
   bottom=['人人都讲你，', '没人真懂你。']),
 'stanley-kubrick': dict(
   h=['越完美的系统，', '越照出人的丑'],
   remind='提醒：他用冷到骨子里的精确，解剖人性最暗的褶皱。',
   left=['2001里，', '一块黑石、一段进化，', '人类刚会拿骨头，', '就学会了杀戮。'],
   right=['他不煽情、不站队，', '只把镜头摆正，', '让体制、战争、欲望', '自己显出荒诞。'],
   contra='把人放进绝对理性里，剩下的才是真人性。',
   bottom=['机器越像人，', '人越像机器。']),
 'takeshi-kitano': dict(
   h=['静到极点，', '突然就爆了'],
   remind='提醒：他用大段留白攒张力，暴力只肯给一秒。',
   left=['花火里，', '两个将死的人开车看海，', '不说话，', '比任何告白都重。'],
   right=['他删掉所有多余，', '让空镜、让停顿', '自己长出情绪——', '然后一刀致命。'],
   contra='克制到极致，爆发才有重量。',
   bottom=['不响的炮，', '最吓人。']),
 'wong-kar-wai': dict(
   h=['时间过期，', '味道才出来'],
   remind='提醒：他拍的不是爱情，是没说出口、也没机会说的那些。',
   left=['重庆森林里，', '罐头会过期、感情会过期，', '只有城市的灯', '替人记着孤单。'],
   right=['他让色彩说话、', '让慢镜沉醉，', '暧昧比确定更美——', '因为你永远差一步。'],
   contra='最美的瞬间，往往是你没抓住的那一个。',
   bottom=['有些话，', '过期了才动听。']),
 'yasujiro-ozu': dict(
   h=['家常一坐，', '就是一生'],
   remind='提醒：他不拍大事，只把饭碗、电车、父女对话拍成永恒。',
   left=['东京物语里，', '老父母来看孩子，', '儿女各自忙碌，', '空荡的房间', '比台词更沉。'],
   right=['低机位、固定镜，', '像跪坐陪你吃饭——', '平淡里，', '藏着最深的离别。'],
   contra='最动人的生活，往往没有什么发生。',
   bottom=['日子平平，', '却再回不去。']),
 'abbas-kiarostami': dict(
   h=['真实与虚构，', '只隔一层雾'],
   remind='提醒：他让孩子、道路、对话自己生长，导演退到幕后。',
   left=['何处是我朋友的家，', '一个小男孩翻山找作业本，', '没有英雄、没有反转，', '真实本身已足够动人。'],
   right=['他模糊纪录片与剧情，', '让观众自己判断', '哪句是真、哪句是演——', '参与，才是看电影的起点。'],
   contra='不演的表演，比精心设计更戳人。',
   bottom=['最真的故事，', '往往看起来像真的。']),
}

# ---------- 卡片绘制 ----------
M = 70
CW = W - M * 2

def meta_text(tid):
    return '25位电影大师在线 | 支持多轮深度追问'

SLOGANS = [
    '来一场跟电影大师最密切的对话',
    '把导演请进你的深夜放映厅',
    '与伟大导演共度一刻钟',
    '让百年光影，回答你今天的问题',
    '和电影巨匠，聊点真东西',
]
def slogan(tid):
    i = int(hashlib.md5(tid.encode()).hexdigest(), 16) % len(SLOGANS)
    return SLOGANS[i]

def draw_card(c, tid, cn, measure=False):
    H = 2800
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img, 'RGBA')
    y = 56

    d.rectangle([M, y, W - M, y + 7], fill=INK); y += 34
    slo = slogan(tid)
    tf, _ = fit_font(slo, REGULAR, 31, 22, CW, spacing=2)
    tw = sum(d.textlength(ch, font=tf) for ch in slo)
    d.text(((W - tw) / 2, y), slo, font=tf, fill=INK); y += 52
    d.rectangle([M, y, W - M, y + 2], fill=INK); y += 44

    for line in c['h']:
        hf, _ = fit_font(line, HEAVY, 96, 52, CW)
        d.text((M, y), line, font=hf, fill=INK)
        y += int(hf.size * 1.28)
    y += 26

    d.text((M, y), meta_text(tid), font=font(HEAVY, 33), fill=INK); y += 54
    rf = font(REGULAR, 28)
    for ln in wrap(c['remind'], rf, CW):
        d.text((M, y), ln, font=rf, fill=GRAY); y += 44
    y += 26

    ph_h = 440
    pf = os.path.join(PORTRAITS, tid + '.jpg')
    if os.path.exists(pf):
        try:
            p = Image.open(pf).convert('RGB')
            cen = smart_centering(p, CW, ph_h, tid)
            p = ImageOps.fit(p, (CW, ph_h), method=Image.LANCZOS, centering=cen)
            img.paste(p, (M, int(y)))
        except Exception:
            d.rectangle([M, y, W - M, y + ph_h], fill=BOX)
    else:
        d.rectangle([M, y, W - M, y + ph_h], fill=BOX)
    y += ph_h + 44

    col_w = W // 2 - M - 34
    y0 = y
    for ci, col in enumerate((c['left'], c['right'])):
        x = M if ci == 0 else W // 2 + 34
        yy = y
        for ln in col:
            if ln == '': yy += 22; continue
            f2, _ = fit_font(ln, REGULAR, 29, 20, col_w)
            d.text((x, yy), ln, font=f2, fill=(44, 42, 40, 255))
            yy += 48
        y = max(y, yy)
    d.rectangle([W // 2 - 1, y0, W // 2 + 1, y + 6], fill=(180, 176, 170, 255))
    y += 52

    bf = font(REGULAR, 29)
    hbf = font(HEAVY, 29)
    body = wrap(c['contra'], bf, CW - 60 - d.textlength(LABEL_CONTRA, font=hbf))
    box_h = len(body) * 46 + 54
    d.rounded_rectangle([M, y, W - M, y + box_h], radius=10, fill=BOX)
    tx = M + 30; ty = y + 27
    d.text((tx, ty), LABEL_CONTRA, font=hbf, fill=INK)
    tx += d.textlength(LABEL_CONTRA, font=hbf)
    for i, ln in enumerate(body):
        if i > 0: tx = M + 30
        d.text((tx, ty), ln, font=bf, fill=INK)
        ty += 46
    y += box_h + 58

    for line in c['bottom']:
        gf, _ = fit_font(line, HEAVY, 68, 40, CW)
        d.text((M, y), line, font=gf, fill=INK)
        y += int(gf.size * 1.3)
    y += 56

    d.rectangle([M, y, W - M, y + 2], fill=(190, 186, 180, 255)); y += 34
    qs = 168
    img.paste(qr_png(f'{BASE}/?director={tid}', qs), (M, int(y)))
    tx = M + qs + 34; ty = y + 12
    d.text((tx, ty), f'长按扫码，与「{cn}」继续对话', font=font(HEAVY, 34), fill=INK); ty += 56
    d.text((tx, ty), BASE, font=font(REGULAR, 25), fill=GRAY); ty += 42
    d.text((tx, ty), '合作交流加微信：fuping394319746', font=font(REGULAR, 25), fill=GRAY); ty += 34
    y = max(y + qs, ty) + 30

    if measure: return y
    return img.crop((0, 0, W, int(y)))

# ---------- 执行 ----------
data = json.load(open(os.path.join(HERE, '..', 'directors.json'), encoding='utf-8'))
directors = [s for s in data['directors'] if s['name'] in CARDS]
print(f'载入导演 {len(directors)} 位，导出目录 -> {OUT}')

if CHECK:
    TW, TH, COLS = 380, 200, 5
    sheet = Image.new('RGB', (COLS * TW, ((len(directors) + COLS - 1) // COLS) * (TH + 30)), (250, 250, 250))
    dd = ImageDraw.Draw(sheet)
    for i, s in enumerate(directors):
        tid = s['name']
        p = Image.open(os.path.join(PORTRAITS, tid + '.jpg')).convert('RGB')
        cen = smart_centering(p, TW, TH, tid)
        c = ImageOps.fit(p, (TW, TH), method=Image.LANCZOS, centering=cen)
        x, yy = (i % COLS) * TW, (i // COLS) * (TH + 30)
        sheet.paste(c, (x, yy))
        dd.text((x + 6, yy + TH + 6), tid, fill=(0, 0, 0))
    out = os.path.join(OUT, '_check.png')
    sheet.save(out)
    print('拼图 ->', out)
else:
    items = []
    for i, s in enumerate(directors, 1):
        tid = s['name']
        cn = cn_name(s.get('display_name', tid))
        img = draw_card(CARDS[tid], tid, cn)
        fn = os.path.join(OUT, tid + '.png')
        img.save(fn)
        items.append((cn, f'{BASE}/?director={tid}', os.path.basename(fn)))
        print(f'  [{i:2d}/{len(directors)}] {tid:22s} -> {fn}')

    cards_html = '\n'.join(
        f'<div class="c"><img src="{fn}" loading="lazy"><div class="meta"><b>{t}</b>'
        f'<code>{u}</code><a href="{u}" target="_blank">打开链接 ↗</a></div></div>'
        for t, u, fn in items)
    html = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<title>导演沙龙 · 引流卡片预览</title><style>
body{{font-family:-apple-system,"PingFang SC",sans-serif;background:#1c1611;margin:0;padding:30px;color:#eee}}
h1{{font-size:24px;margin:0 0 6px}}p{{opacity:.6;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px}}
.c{{background:#2b2118;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.c img{{width:100%;display:block}}.meta{{padding:12px 14px}}.meta b{{font-size:18px}}
code{{display:block;font-size:11px;opacity:.5;margin:6px 0;word-break:break-all}}
a{{color:#e9c46a;font-size:13px;text-decoration:none}}</style></head>
<body><h1>导演沙龙 · 引流知识卡片</h1>
<p>共 {len(directors)} 张 · 扫码即选中对应导演（深链 ?director=id）</p>
<div class="grid">{cards_html}</div></body></html>'''
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
    print('画廊 ->', os.path.join(OUT, 'index.html'))
