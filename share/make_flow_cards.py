#!/usr/bin/env python3
# 生成「思想会客厅」爆款引流知识卡片（杂志排版风：大标题+照片+双栏+反常识观点+金句+二维码）
# 用法: python3 make_flow_cards.py [访问地址]
# 产物: share/cards/<thinker-id>.png (25 张) + share/cards/index.html (预览画廊)
# 肖像: share/posters/portraits/<id>.jpg（复用已有素材；缺图自动用纯色块占位）

import os, sys, json, hashlib
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://nuwa-h5.onrender.com'
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

# ---------- 字体：在 PingFang.ttc 里探测 Semibold（重标题）/ Regular（正文） ----------
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

# 智能裁切：在原图上滑动纵向窗口，选“边缘能量最高”（人脸/主体所在）的窗口；顶部略加权防切头
# 逐人微调：CROP_Y[id] 强制指定窗口纵向位置 0(贴顶)~1(贴底)
CROP_Y = {
    'elon-musk': 0.02,
    'steve-jobs': 0.14,
    'kazuo-inamori': 0.12,
    'wang-yangming': 0.50,
    'sun-tzu': 0.38,
    'sima-qian': 0.45,
    'marie-curie': 0.22,
    'coco-chanel': 0.10,
    'friedrich-hayek': 0.08,
    'liqingzhao': 0.22,
    'socrates': 0.12,
    'zhang-yiming': 0.42,
    'richard-feynman': 0.12,
    'sam-altman': 0.15,
    'daniel-kahneman': 0.10,
    'charlie-munger': 0.16,
}

# 画作类肖像：不裁切，整幅等比放入相框，两侧垫取自画芯边缘的底色（避免窄高画被横裁得只剩半张脸）
PAD_IDS = {'sun-tzu', 'wang-yangming', 'sima-qian', 'socrates', 'confucius', 'laozi', 'liqingzhao'}

def edge_color(p):
    # 只采样顶部边缘（画作上方留白/底色），避免取到衣袍等主体色
    px = p.load(); w, h = p.size
    rs = gs = bs = n = 0
    for x in range(0, w, max(1, w // 40)):
        for yy in range(2, min(8, h)):
            r, g, b = px[x, yy][:3]
            rs += r; gs += g; bs += b; n += 1
    return (rs // n, gs // n, bs // n)

def place_photo(p, tw, th, tid):
    """返回 (已处理成 tw×th 的图片)。PAD_IDS 内整幅缩放垫底，其余智能裁切。"""
    if tid in PAD_IDS:
        pw, ph0 = p.size
        s = min(tw / pw, th / ph0)
        nw, nh = max(1, int(pw * s)), max(1, int(ph0 * s))
        pr = p.resize((nw, nh), Image.LANCZOS)
        bg = Image.new('RGB', (tw, th), edge_color(p))
        bg.paste(pr, ((tw - nw) // 2, (th - nh) // 2))
        return bg
    cen = smart_centering(p, tw, th, tid)
    return ImageOps.fit(p, (tw, th), method=Image.LANCZOS, centering=cen)

def smart_centering(img, tw, th, tid):
    W0, H0 = img.size
    if tid in CROP_Y:
        return (0.5, CROP_Y[tid])
    ch = W0 * th / tw            # 目标裁切窗口在原图尺度上的高
    if ch >= H0:                 # 竖构图：横向滑动，纵向全保留
        return (0.5, 0.5)
    g = img.convert('L').resize((60, 60))
    e = g.filter(ImageFilter.FIND_EDGES)
    px = e.load()
    rows = [sum(px[x, y] for x in range(60)) for y in range(60)]
    win = max(2, round(60 * ch / H0))
    best, best_top = -1, 0
    for top in range(0, 60 - win + 1):
        s = sum(rows[top:top + win]) * (1 + 0.35 * (1 - top / 60))  # 顶部偏置
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

# ---------- 每位大师的卡片文案 ----------
CARDS = {
 'charlie-munger': dict(
   tag='关于多元思维与逆向思考的底层逻辑',
   h=['聪明人为什么', '总在反着想问题'],
   remind='提醒：真正拉开决策差距的，不是知道得多，而是少犯蠢。',
   left=['如果我知道我会死在哪里，', '我就永远不去那个地方。', '', '投资、择业、婚姻，', '先想清楚怎样必然失败，', '再绕开那条路。'],
   right=['真正的能力圈，', '不是你知道什么，', '而是清楚自己不知道什么。', '', '手里拿着锤子的人，', '看什么都像钉子。'],
   contra='做得好，往往不是因为聪明，而是因为系统地避免了愚蠢。',
   bottom=['少犯蠢，比多聪明', '值钱得多。']),
 'elon-musk': dict(
   tag='关于第一性原理与造物逻辑的底层逻辑',
   h=['把问题拆到原子，', '答案自己会浮现'],
   remind='提醒：多数"不可能"，只是别人没认真算过的物理题。',
   left=['电池贵？拆开看：', '钴、镍、铝、碳……', '按市价一算，原材料只占零头。', '贵的从来不是材料，', '是没人质疑过的组装方式。'],
   right=['第一性原理不是口号，', '是一种狠劲：', '把一切推倒到物理定律，', '再从零往上搭。', '', '行业惯例，只是一种', '没被证伪过的假设。'],
   contra='不是资源决定成败，是你敢不敢把"行业惯例"当成待证伪的假设。',
   bottom=['别在别人的答案里', '找你的问题。']),
 'richard-feynman': dict(
   tag='关于学习、诚实与真懂的底层逻辑',
   h=['讲不明白的知识，', '其实你并没有学会'],
   remind='提醒：检验学习的唯一标准，是能否讲给外行听懂。',
   left=['你记住了公式，', '不代表你理解了知识。', '用最简单的话讲给小孩听，', '哪里卡壳，', '哪里就是你知识体系上的窟窿。'],
   right=['科学家的第一美德，', '是对自己诚实：', '"我不知道"，', '比任何漂亮的解释都珍贵。'],
   contra='笔记做得越漂亮，可能越是在用勤奋掩盖没懂。',
   bottom=['所有装懂的功夫，', '都敌不过一句"讲给我听听"。']),
 'zhang-yiming': dict(
   tag='关于延迟满足与平常心的底层逻辑',
   h=['优秀不是爆发，', '是把平常心用足十年'],
   remind='提醒：多数人高估了三个月的努力，低估了十年的耐心。',
   left=['很多人的问题，', '是既要结果，又要即时满足。', '而延迟满足的本质是：', '把此刻的焦躁，', '换成对规律的耐心。'],
   right=['保持平常心，', '不是躺平，', '是不带情绪地面对现实，', '然后继续做该做的事。'],
   contra='情绪波动最大的时刻，往往就是决策最差的时刻。',
   bottom=['走得远的人，', '都在跟时间做朋友。']),
 'naval-ravikant': dict(
   tag='关于财富、杠杆与自由的底层逻辑',
   h=['打工出卖时间，', '产品化自己才是杠杆'],
   remind='提醒：致富靠的不是出卖时间，而是拥有可复用的资产。',
   left=['出租时间，永远富不起来。', '你要找到那种', '"睡一觉还在替你干活"的东西：', '代码、内容、品牌、资本。'],
   right=['特定知识＝你的天赋＋你的痴迷，', '它无法被培训，', '所以无法被取代。', '', '选择大于努力：', '赛道决定天花板。'],
   contra='拼命努力只能让你达到平均值，选择赛道才决定上限。',
   bottom=['把自己变成产品，', '让钱替你上班。']),
 'steve-jobs': dict(
   tag='关于专注、取舍与美的底层逻辑',
   h=['专注不是决定做什么，', '是对一百个好主意说不'],
   remind='提醒：真正的简洁，不是删掉功能，是穿透复杂后的清晰。',
   left=['苹果做过多少产品？', '数得过来。', '砍掉的多，留下的少，', '留下的每一件，', '都是"不"字堆出来的。'],
   right=['科技要跟人文结合，', '产品才有灵魂。', '用户不知道自己要什么，', '直到你把作品放到他手上。'],
   contra='加功能是本能，砍功能才是本事。',
   bottom=['留在桌面上的，', '必须是你最骄傲的那一件。']),
 'kazuo-inamori': dict(
   tag='关于工作观与利他经营的底层逻辑',
   h=['把自己逼进绝境，', '神明才会出手相助'],
   remind='提醒：答案永远在现场，前提是你真的把自己"沉"进去。',
   left=['极度认真地工作，', '能扭转人生。', '不是工作需要你努力，', '是努力需要一件工作来磨你。'],
   right=['作为人，何谓正确？', '把这一个标准想透，', '经营、人生都不再难选。', '', '完美主义不是苛刻，', '是对结果的敬畏。'],
   contra='先有全力以赴的"因"，才配得上所谓运气的"果"。',
   bottom=['付出不亚于任何人', '的努力，是唯一捷径。']),
 'wang-yangming': dict(
   tag='关于知行合一与心力的底层逻辑',
   h=['懂得再多道理，', '做不到就等于不知道'],
   remind='提醒：真正的知道，是行为的改变；否则只是信息过客。',
   left=['你以为是先"懂"再"做"，', '其实知与行本是一件事：', '没去做的懂，', '是假的懂。'],
   right=['人须在事上磨，', '静坐空想，遇事全塌。', '每一件让你烦躁的小事，', '都是磨心性的砂纸。'],
   contra='你不是缺方法，是缺"事上练"的那一刀。',
   bottom=['心不唤物，', '物不至。']),
 'socrates': dict(
   tag='关于提问、自知与省察的底层逻辑',
   h=['未曾省察的人生，', '根本不值得过'],
   remind='提醒：多数人用忙碌逃避思考，用观点掩盖无知。',
   left=['我唯一知道的，', '就是我一无所知。', '这不是谦虚，是起点：', '承认空杯，才装得下东西。'],
   right=['别急着要答案，', '先学会被追问。', '一层层问下去，', '你以为的"知道"会纷纷塌掉，', '真东西才开始生长。'],
   contra='让你舒服的观点未必对，能经得住追问的才算数。',
   bottom=['会提问的人，', '永远不会被答案困住。']),
 'warren-buffett': dict(
   tag='关于复利、护城河与耐心的底层逻辑',
   h=['人生像滚雪球，', '要找很湿的雪和长坡'],
   remind='提醒：致富的秘密是时间，而多数人偏偏等不起。',
   left=['别人恐惧我贪婪，', '前提是你有清单、有纪律，', '而不是有胆子。', '', '没有护城河的高增长，', '都是替别人做嫁衣。'],
   right=['品牌、成本、转换成本、', '网络效应——', '护城河比城堡重要。', '', '真正的好机会不多，', '等得到，才拿得住。'],
   contra='对不懂的人，分散是保护；对懂的人，过度分散是稀释。',
   bottom=['价格是你付出的，', '价值是你得到的。']),
 'ray-dalio': dict(
   tag='关于原则、犯错与机器思维的底层逻辑',
   h=['痛苦＋反思＝进步，', '这是我唯一的公式'],
   remind='提醒：把人生当机器来调试，情绪是噪声，原则是代码。',
   left=['我一生最大的收获，', '都来自失败之后的那次复盘：', '错在哪？下次怎么判？', '写下来，就成了原则。'],
   right=['极度求真、极度透明，', '听起来刺耳，', '却是进化的唯一方式。', '', '不进化，就退化。'],
   contra='让你痛苦的不是失败本身，是拒绝从失败里提取原则。',
   bottom=['拥抱现实，', '现实会奖励面对它的人。']),
 'confucius': dict(
   tag='关于修身、仁与秩序的底层逻辑',
   h=['君子求诸己，', '小人求诸人'],
   remind='提醒：改变不了的，先修自己；修好自己，边界自然扩大。',
   left=['学而不思则罔，', '思而不学则殆。', '输入和思考，', '从来缺一不可。'],
   right=['己所不欲，勿施于人。', '两千年过去，', '这仍是人际关系', '成本最低的算法。'],
   contra='怨天尤人是最贵的习惯，它让你永远停在原地。',
   bottom=['行有不得，', '皆反求诸己。']),
 'friedrich-nietzsche': dict(
   tag='关于苦难、意志与成为自己的底层逻辑',
   h=['那些杀不死我的，', '会让我更强大'],
   remind='提醒：逃避痛苦的人被痛苦定义，消化痛苦的人自己定义自己。',
   left=['你的痛苦不是问题，', '对痛苦的解释才是。', '同一个伤口，', '有人烂在里面，', '有人长出翅膀。'],
   right=['成为你自己：', '先服从，再怀疑，', '最后亲手重写', '属于你的价值表。'],
   contra='舒适区里的"自我"，往往只是环境的复印件。',
   bottom=['知道为什么而活的人，', '几乎能承受任何一种生活。']),
 'laozi': dict(
   tag='关于无为、柔弱与长期主义的底层逻辑',
   h=['反者道之动：', '退，有时是最快的进'],
   remind='提醒：争一时之胜的人赢局部，不争的人赢终局。',
   left=['上善若水，', '水善利万物而不争。', '不争，不是怂，', '是不在别人定义的赛道上', '消耗自己。'],
   right=['天下难事，必作于易；', '天下大事，必作于细。', '别迷信惊天动地的决心，', '要相信今天那一小步。'],
   contra='用力过猛，往往是内心虚弱的表现。',
   bottom=['胜人者有力，', '自胜者强。']),
 'marie-curie': dict(
   tag='关于专注、信念与枯燥的底层逻辑',
   h=['伟大不在天分，', '在无人喝彩时的日复一日'],
   remind='提醒：所有突破，都是长期单调重复的复利。',
   left=['在漏雨的棚屋里，', '搅拌几吨沥青矿渣，', '四年，只为提炼0.1克镭。', '科学的美，', '是用枯燥喂出来的。'],
   right=['生活中没有可怕的东西，', '只有需要理解的东西。', '理解它，', '恐惧就变成了地图。'],
   contra='天赋决定起点，对枯燥的忍耐力决定终点。',
   bottom=['把注意力放对地方，', '时间会给你答案。']),
 'daniel-kahneman': dict(
   tag='关于直觉、偏差与决策的底层逻辑',
   h=['你的直觉，', '可能只是惯性的错觉'],
   remind='提醒：大脑有两套系统，犯错时往往是快思考在替你拍板。',
   left=['快思考省电但爱编故事，', '慢思考准确但懒得上班。', '重大决策前，先问一句：', '我是在思考，还是在联想？'],
   right=['锚定、框架、损失厌恶……', '你不是不理性，', '你是可预测地不理性。', '预测到，就能防。'],
   contra='自信程度和正确率，几乎是两回事。',
   bottom=['对自己的直觉越笃定，', '越要多留一个心眼。']),
 'sun-tzu': dict(
   tag='关于竞争、胜负与不战的底层逻辑',
   h=['百战百胜，', '不是善之善者也'],
   remind='提醒：最高明的赢，是让胜利在开打之前就已注定。',
   left=['上兵伐谋，其次伐交，', '其次伐兵，其下攻城。', '硬仗是下策，', '打之前先想：', '这仗能不能不打？'],
   right=['知己知彼者，百战不殆。', '多数人的问题不是不了解对手，', '是不敢看清自己。'],
   contra='赢家不是打得多漂亮，而是根本不打没必要打的仗。',
   bottom=['胜兵先胜，', '而后求战。']),
 'jensen-huang': dict(
   tag='关于长期押注与穿越周期的底层逻辑',
   h=['战略耐心，', '是把一件事做穿三十年的狠'],
   remind='提醒：风口人人看得见，熬得住无人区的人才有门票。',
   left=['赌通用计算赌了很多年，', '股价跌掉八成也没回头。', '不是头铁，', '是算得清十年后的世界', '需要什么。'],
   right=['"我们离倒闭还有30天"——', '不是焦虑，是清醒：', '让组织永远保持', '创业第一天的灵敏度。'],
   contra='真正的护城河不是领先，而是领先了还拼命。',
   bottom=['在无人区先走十年，', '才有资格谈风口。']),
 'coco-chanel': dict(
   tag='关于风格、自由与打破规则的底层逻辑',
   h=['时尚易逝，', '风格永存'],
   remind='提醒：别用别人的目光定义美，风格是从"我是谁"里长出来的。',
   left=['她把女性从束腰里解放出来，', '不是因为叛逆，', '是因为她先想清楚了：', '衣服是为人服务的，', '不是反过来。'],
   right=['优雅是拒绝的艺术。', '懂得舍弃，', '才留得住真正的质感。'],
   contra='跟风买来的时髦是消费，长在自己身上的才是风格。',
   bottom=['想要无可取代，', '就必须与众不同。']),
 'nassim-taleb': dict(
   tag='关于不确定性、反脆弱与生存的底层逻辑',
   h=['强韧的反面不是脆弱，', '是怕折腾'],
   remind='提醒：预测黑天鹅没有用，让自己"受伤后更强"才有用。',
   left=['风吹灭蜡烛，却助长大火。', '你要做的不是躲风，', '是成为那堆火：', '用适度冲击，', '喂大自己的反脆弱性。'],
   right=['杠铃策略：', '九成极度保守，', '一成极度冒险，', '拒绝中间那种', '"看起来稳妥"的平庸风险。'],
   contra='稳定的工作可能是最大的风险，波动里反而藏着安全。',
   bottom=['杀不死你的，', '最好让你更强——前提是你别躲。']),
 'sima-qian': dict(
   tag='关于隐忍、书写与历史视角的底层逻辑',
   h=['究天人之际，', '通古今之变'],
   remind='提醒：把时间尺度拉长到百年，眼前的输赢会完全变样。',
   left=['受了最羞辱的刑罚，', '却选择隐忍苟活，', '只为把这部书写完。', '有些活着，', '比死需要更大的勇气。'],
   right=['读史的价值不是记典故，', '是获得一种尺度：', '在更长的时间里，', '看清什么是表象，', '什么是趋势。'],
   contra='当下的评价体系，往往配不上真正重要的事。',
   bottom=['人固有一死，', '或重于泰山，或轻于鸿毛。']),
 'sam-altman': dict(
   tag='关于创业、复利与想大做小的底层逻辑',
   h=['想大，做小，', '然后每天复利一点点'],
   remind='提醒：趁便宜的时候买长期——包括技能、关系和信誉。',
   left=['复利不只在钱上：', '技能、人脉、声誉，', '都会复利。', '而绝大多数人，', '从不给它们时间。'],
   right=['创业第一步不是想商业模式，', '是找一个别人还没注意到的趋势，', '然后全力押上去。'],
   contra='"快速试错"的真正含义是降低试错成本，而不是鼓励失败。',
   bottom=['在长坡上，', '每天滚一点点雪球。']),
 'liqingzhao': dict(
   tag='关于才情、困境与自我表达的底层逻辑',
   h=['生当作人杰，', '死亦为鬼雄'],
   remind='提醒：逆境夺走的只是境遇，夺不走一个人定义自己的权利。',
   left=['国破、家亡、夫死、', '藏品散尽，', '她把这一切都写进了词里。', '痛苦不能选择，', '但怎么消化痛苦可以选择。'],
   right=['"词别是一家"——', '她敢跟整个时代的审美叫板，', '因为她的标准，', '来自千锤百炼的实践。'],
   contra='真正的表达欲不是展示自己，是先说服自己。',
   bottom=['被记住的作品，', '都先打败了写它的那个绝境。']),
 'friedrich-hayek': dict(
   tag='关于秩序、知识与自由的底层逻辑',
   h=['没有人能规划出', '一个真实的复杂世界'],
   remind='提醒：分散在千万人头脑中的知识，永远大于任何单一头脑。',
   left=['价格不是商人定的，', '是千万次选择汇成的信号。', '轻视它的人，', '终将被它纠正。'],
   right=['好秩序是"长"出来的，', '不是"设计"出来的。', '尊重演化，', '好过迷信蓝图。'],
   contra='"看得见的手"每解决一个问题，可能正在制造三个看不见的问题。',
   bottom=['对复杂世界保持谦卑，', '是智慧的开始。']),
 'john-maynard-keynes': dict(
   tag='关于预期、需求与不确定性的底层逻辑',
   h=['长期来看我们都死了，', '所以短期必须活得清醒'],
   remind='提醒：市场保持非理性的时间，可能比你撑住的时间更长。',
   left=['经济不是一台', '自动回归均衡的机器，', '它由预期驱动：', '人们相信什么，', '什么就会发生。'],
   right=['动物精神——', '那些无法计算的信心与恐惧，', '恰恰是波动真正的引擎。'],
   contra='用"长期正确"安慰自己，常常是逃避短期纠错的借口。',
   bottom=['在不确定性里活着，', '先承认自己不知道明天。']),
}

# ---------- 卡片绘制 ----------
M = 70           # 左右边距
CW = W - M * 2   # 内容宽

def meta_text(tid):
    return '25位大师在线 | 支持多轮深度追问'

# 顶部引流 slogan：统一“与大师对话”调性，每卡按 id 稳定分配一条
SLOGANS = [
    '来一场跟思想大师最密切的对话',
    '把大师请进你的深夜思考',
    '与伟大头脑共度一刻钟',
    '让百年智慧，回答你今天的问题',
    '和思想巨匠，聊点真东西',
]
def slogan(tid):
    i = int(hashlib.md5(tid.encode()).hexdigest(), 16) % len(SLOGANS)
    return SLOGANS[i]

def draw_card(c, tid, cn, measure=False):
    H = 2800  # 先画在大画布上，最后按实际内容高度裁切
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img, 'RGBA')
    y = 56

    # 顶部粗线 + 小标语 + 细线
    d.rectangle([M, y, W - M, y + 7], fill=INK); y += 34
    slo = slogan(tid)
    tf, _ = fit_font(slo, REGULAR, 31, 22, CW, spacing=2)
    tw = sum(d.textlength(ch, font=tf) for ch in slo)
    d.text(((W - tw) / 2, y), slo, font=tf, fill=INK); y += 52
    d.rectangle([M, y, W - M, y + 2], fill=INK); y += 44

    # 大标题（左对齐，自动缩号）
    for line in c['h']:
        hf, _ = fit_font(line, HEAVY, 96, 52, CW)
        d.text((M, y), line, font=hf, fill=INK)
        y += int(hf.size * 1.28)
    y += 26

    # 阅读信息 + 提醒
    d.text((M, y), meta_text(tid), font=font(HEAVY, 33), fill=INK); y += 54
    rf = font(REGULAR, 28)
    for ln in wrap(c['remind'], rf, CW):
        d.text((M, y), ln, font=rf, fill=GRAY); y += 44
    y += 26

    # 照片（4:3 裁切）
    ph_h = 440
    pf = os.path.join(PORTRAITS, tid + '.jpg')
    if os.path.exists(pf):
        try:
            p = Image.open(pf).convert('RGB')
            img.paste(place_photo(p, CW, ph_h, tid), (M, int(y)))
        except Exception:
            d.rectangle([M, y, W - M, y + ph_h], fill=BOX)
    else:
        d.rectangle([M, y, W - M, y + ph_h], fill=BOX)
    y += ph_h + 44

    # 双栏正文 + 竖分隔线
    col_w = W // 2 - M - 34
    cf = font(REGULAR, 29)
    col_top = y
    for ci, col in enumerate((c['left'], c['right'])):
        x = M if ci == 0 else W // 2 + 34
        yy = y
        for ln in col:
            if ln == '': yy += 22; continue
            f2, _ = fit_font(ln, REGULAR, 29, 20, col_w)
            d.text((x, yy), ln, font=f2, fill=(44, 42, 40, 255))
            yy += 48
        y = max(y, yy)
    d.rectangle([W // 2 - 1, col_top, W // 2 + 1, y + 6], fill=(180, 176, 170, 255))
    y += 52

    # 反常识观点框
    bf = font(REGULAR, 29)
    hbf = font(HEAVY, 29)
    body = wrap(c['contra'], bf, CW - 60 - d.textlength('反常识观点：', font=hbf))
    box_h = len(body) * 46 + 54
    d.rounded_rectangle([M, y, W - M, y + box_h], radius=10, fill=BOX)
    tx = M + 30; ty = y + 27
    d.text((tx, ty), '反常识观点：', font=hbf, fill=INK)
    tx += d.textlength('反常识观点：', font=hbf)
    for i, ln in enumerate(body):
        if i > 0: tx = M + 30
        d.text((tx, ty), ln, font=bf, fill=INK)
        ty += 46
    y += box_h + 58

    # 底部金句（大号重体）
    for line in c['bottom']:
        gf, _ = fit_font(line, HEAVY, 68, 40, CW)
        d.text((M, y), line, font=gf, fill=INK)
        y += int(gf.size * 1.3)
    y += 56

    # 页脚：二维码 + 引流文案
    d.rectangle([M, y, W - M, y + 2], fill=(190, 186, 180, 255)); y += 34
    qs = 168
    img.paste(qr_png(f'{BASE}/?thinker={tid}', qs), (M, int(y)))
    tx = M + qs + 34; ty = y + 12
    d.text((tx, ty), f'长按扫码，与「{cn}」继续对话', font=font(HEAVY, 34), fill=INK); ty += 56
    d.text((tx, ty), BASE, font=font(REGULAR, 25), fill=GRAY); ty += 42
    d.text((tx, ty), '合作交流加微信：fuping394319746', font=font(REGULAR, 25), fill=GRAY); ty += 34
    y = max(y + qs, ty) + 30

    if measure: return y
    return img.crop((0, 0, W, int(y)))

# ---------- 执行 ----------
skills = json.load(open(os.path.join(HERE, '..', 'skills.json'), encoding='utf-8'))['skills']
thinkers = [s for s in skills if s['name'] in CARDS]
print(f'载入思想家 {len(thinkers)} 位，开始生成卡片 → {OUT}')
items = []
for i, s in enumerate(thinkers, 1):
    tid = s['name']
    cn = cn_name(s.get('display_name', tid))
    img = draw_card(CARDS[tid], tid, cn)
    fn = os.path.join(OUT, tid + '.png')
    img.save(fn)
    items.append((cn, f'{BASE}/?thinker={tid}', os.path.basename(fn)))
    print(f'  [{i:2d}/{len(thinkers)}] {tid:22s} -> {fn}')

cards_html = '\n'.join(
    f'<div class="c"><img src="{fn}" loading="lazy"><div class="meta"><b>{t}</b>'
    f'<code>{u}</code><a href="{u}" target="_blank">打开链接 ↗</a></div></div>'
    for t, u, fn in items)
html = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<title>思想会客厅 · 引流卡片预览</title><style>
body{{font-family:-apple-system,"PingFang SC",sans-serif;background:#1c1611;margin:0;padding:30px;color:#eee}}
h1{{font-size:24px;margin:0 0 6px}}p{{opacity:.6;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px}}
.c{{background:#2b2118;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.c img{{width:100%;display:block}}.meta{{padding:12px 14px}}.meta b{{font-size:18px}}
code{{display:block;font-size:11px;opacity:.5;margin:6px 0;word-break:break-all}}
a{{color:#e9c46a;font-size:13px;text-decoration:none}}</style></head>
<body><h1>思想会客厅 · 引流知识卡片</h1>
<p>共 {len(thinkers)} 张 · 扫码即选中对应大师（深链 ?thinker=id）</p>
<div class="grid">{cards_html}</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
print('画廊 ->', os.path.join(OUT, 'index.html'))
