#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""播客访谈视频 · 生成流水线（中/英双语）

数据源：
  podcast_data.py      中文（唯一源，含逐段表演提示 stage）
  podcast_data_en.py   英文（台词为地道英文口语改写，非直译）

产出：
  prompts/<id>/NN-<段名>.txt      中文逐段提示词（直接喂视频模型）
  prompts-en/<id>/NN-<title>.txt  英文逐段提示词
  podcast-scripts.md             中文合集文档
  podcast-scripts-en.md          英文合集文档

用法:
    python3 make_podcast_prompts.py                 # 中+英 全量
    python3 make_podcast_prompts.py --lang zh       # 只中文
    python3 make_podcast_prompts.py --lang en       # 只英文（海外投放 / 英文配音）
    python3 make_podcast_prompts.py --md-only       # 只更新文档
    python3 make_podcast_prompts.py --guest laozi sun-tzu   # 只生成指定嘉宾
"""

import os
import re
import sys

import podcast_data as ZH
import podcast_data_en as EN

HERE = os.path.dirname(os.path.abspath(__file__))

# 英文数据未逐段写 stage，用这两条通用表演提示兜底
DEFAULT_STAGE_EN = (
    "Both stay in the medium two-shot throughout; the guest answers with small head or hand movements "
    "while the host listens without interrupting. Keep 1~2 seconds of silence between lines."
)
DEFAULT_STAGE_EN_END = (
    "The host closes the tablet and visibly relaxes; the guest falls silent after the last line. "
    "Both hold a final 3-second silence before the shot ends."
)

LABEL = {
    'zh': {
        'env': '**环境**', 'camera': '**机位与表演**', 'host': '**主持人（"我"，左边人物）**',
        'voice': '**声音**', 'style': '**风格与输出**', 'open': '**开场句（复用）**',
        'head': '**片头（3 秒，系列统一）**', 'persona': '**形象卡**', 'manner': '**说话方式**',
        'guest_voice': '**声音**', 'q': '**问', 'make': '## 制作与投放', 'link': '| 嘉宾 | 深链 |',
        'chain': '|', 'table': '|---|---|',
    },
    'en': {
        'env': '**Environment**', 'camera': '**Camera & Performance**', 'host': '**Host ("me", left of frame)**',
        'voice': '**Voice**', 'style': '**Style & Output**', 'open': '**Opening line (shared)**',
        'head': '**Cold open (3s, shared by the whole series)**', 'persona': '**Character**',
        'manner': '**Manner of speaking**', 'guest_voice': '**Voice**', 'q': '**Q',
        'make': '## Production & Distribution', 'link': '| Guest | Deep link |',
        'chain': '|', 'table': '|---|---|',
    },
}


def safe(name: str) -> str:
    s = re.sub(r'[\\/:*?"<>|\s,.\']+', '-', name)
    return re.sub(r'-+', '-', s).strip('-') or 'seg'


def guest_list(lang):
    if lang == 'zh':
        return ZH.GUESTS
    order = [g['id'] for g in ZH.GUESTS]
    return [dict(EN.GUESTS_EN[i], id=i) for i in order if i in EN.GUESTS_EN]


def common_of(lang):
    return ZH.COMMON if lang == 'zh' else EN.COMMON_EN


def landing(lang):
    return ZH.LANDING


def seg_prompt(lang, g, title, stage, lines, dur):
    C = common_of(lang)
    name = g['name']
    if lang == 'zh':
        head = (f'写实播客访谈视频，16:9 横屏，专业电影摄影机拍摄，固定机位中景，'
                f'两人同框，画面稳定。约 {dur} 秒。')
        tail = ('注意：台词之间保留 1~2 秒静默停顿，不要一口气念完；'
                '人物在整段中保持不动，仅头部与手部有细微动作。')
        labels = ['【环境】', '【主持人（画面左侧）】', f'【嘉宾：{name}（画面右侧）】',
                  '【镜头与表演】', '【台词】', '【声音】', '【风格】']
        manner_line = f'说话方式：{g["manner"]}'
    else:
        head = ("Realistic podcast interview video, 16:9 landscape, shot on a professional cinema camera, "
                "locked-off medium two-shot, both people in frame, steady. About %d seconds." % dur)
        tail = ("Note: leave 1~2 seconds of silence between lines — do not rush through them. "
                "Both stay seated throughout, with only subtle head and hand movement.")
        labels = ['[ENVIRONMENT]', '[HOST — left of frame]', f'[GUEST: {name} — right of frame]',
                  '[CAMERA & PERFORMANCE]', '[DIALOGUE]', '[VOICE]', '[STYLE]']
        manner_line = f'Manner of speaking: {g["manner"]}'

    sep = ' ' if lang == 'en' else ''
    out = [head, '', f'{labels[0]}{sep}{C["env"]}', '', f'{labels[1]}{sep}{C["host"]}', '',
           f'{labels[2]}{sep}{g["persona"]}', manner_line, '',
           f'{labels[3]}{sep}{C["camera"]}',
           (f'本段具体要求：{stage}' if lang == 'zh' else f'This segment: {stage}'), '',
           labels[4]]
    out += [f'{w}：{t}' if lang == 'zh' else f'{w}: {t}' for w, t in lines]
    out += ['', f'{labels[5]}{sep}{C["host_voice"]} {g["voice"]}',
            f'{labels[6]}{sep}{C["style"]}', '', tail]
    return '\n'.join(out)


def head_prompt(lang, g):
    C = common_of(lang)
    if lang == 'zh':
        body = ('【画面内容】开场空镜：播客间内暂时无人，两把皮椅与中间小边几上的两杯清水入镜，'
                '书架灯带暖光稳定，画面完全静止。随后主持人从左侧入座，嘉宾已坐在右侧等待。'
                '无人物特写、无运镜，只是一次安静的落座。')
        return '\n'.join([
            '写实播客访谈视频，16:9 横屏，专业电影摄影机拍摄，固定机位中景，约 3 秒。', '',
            f'【环境】{C["env"]}', '', body, '', f'【风格】{C["style"]}', '',
            '（本段为系列统一片头，所有嘉宾共用，用于建立节目辨识度）'])
    body = ("[CONTENT] Cold open: the studio is momentarily empty — the two armchairs and the small side table "
            "with two glasses of water are in frame, the shelf lighting is steady, the frame completely still. "
            "Then the host enters from the left and sits; the guest is already seated on the right. "
            "No close-ups, no camera movement — simply a quiet settling into the chairs.")
    return '\n'.join([
        "Realistic podcast interview video, 16:9 landscape, shot on a professional cinema camera, "
        "locked-off medium shot, about 3 seconds.", '',
        f'[ENVIRONMENT]{C["env"]}', '', body, '', f'[STYLE]{C["style"]}', '',
        "(Shared cold open for the whole series — used to build recognition.)"])


def write_prompts(lang, g):
    out_dir = os.path.join(HERE, 'prompts' if lang == 'zh' else 'prompts-en')
    d = os.path.join(out_dir, g['id'])
    os.makedirs(d, exist_ok=True)
    C = common_of(lang)
    files = []

    p = os.path.join(d, '00-片头.txt' if lang == 'zh' else '00-cold-open.txt')
    open(p, 'w', encoding='utf-8').write(head_prompt(lang, g))
    files.append(p)

    lines = [(w, t.replace('{X}', g['name'])) for w, t in C['opening_lines']]
    p = os.path.join(d, '01-开场.txt' if lang == 'zh' else '01-opening.txt')
    open(p, 'w', encoding='utf-8').write(
        seg_prompt(lang, g, 'opening', C['opening_stage'], lines, C['opening_dur']))
    files.append(p)

    for i, q in enumerate(g['q'], start=2):
        stage = q.get('stage') or (DEFAULT_STAGE_EN if lang == 'en' else COMMON_FALLBACK_ZH)
        p = os.path.join(d, f'{i:02d}-{safe(q["t"])}.txt')
        open(p, 'w', encoding='utf-8').write(seg_prompt(lang, g, q['t'], stage, q['lines'], 14))
        files.append(p)

    e = g['ending']
    stage = e.get('stage') or (DEFAULT_STAGE_EN_END if lang == 'en' else COMMON_FALLBACK_ZH)
    p = os.path.join(d, f'{len(g["q"]) + 2:02d}-{safe(e["t"])}.txt')
    open(p, 'w', encoding='utf-8').write(
        seg_prompt(lang, g, e['t'], stage, e['lines'], e.get('dur', 13)))
    files.append(p)

    merged = [open(f, encoding='utf-8').read() for f in files]
    mp = os.path.join(d, ('ALL-%s.md' % safe(g['name'])))
    title = (f'# {g["name"]} · 播客访谈视频 全段提示词'
             if lang == 'zh' else f'# {g["name"]} · Podcast Video — Full Segment Prompts')
    open(mp, 'w', encoding='utf-8').write(title + '\n\n' + '\n\n---\n\n'.join(merged))
    return files + [mp]


COMMON_FALLBACK_ZH = '两人在中景双人同框中保持坐姿，嘉宾回答时有轻微的头部或手部动作，主持人聆听不打断；台词之间保留 1~2 秒静默。'


def build_md(lang):
    C = common_of(lang)
    L = LABEL[lang]
    md = os.path.join(HERE, 'podcast-scripts.md' if lang == 'zh' else 'podcast-scripts-en.md')
    src = '`podcast_data.py`' if lang == 'zh' else '`podcast_data_en.py`'
    L_ = [f'# {C["title"]}', '',
          ('> 本文件由 `make_podcast_prompts.py` 从 %s 自动生成，请勿手改。' % src if lang == 'zh'
           else '> Auto-generated by `make_podcast_prompts.py` from %s — do not edit by hand.' % src),
          ('> 改数据后重新运行脚本即可。' if lang == 'zh' else '> Edit the data and re-run the script.'), '']
    if lang == 'zh':
        L_ += ['同一档节目：**同一个播客间、同一个机位、同一位主持人（我）、换不同嘉宾**。',
               '用于 AI 视频逐段生成（5~10s 一段）后拼接，片尾挂思想会客厅深链导流。']
    else:
        L_ += ["One show: **the same studio, the same camera, the same host (me) — a different guest each time.**",
               "Generate segment by segment (5~10s each) and cut them together; the closing card carries the "
               "salon deep link."]
    L_ += ['', '---', '', (L['env']), C['env'], '', (L['camera']), C['camera'], '',
           (L['host']), C['host'], '', (L['voice']), C['host_voice'],
           ('嘉宾声音见各篇。' if lang == 'zh' else 'Guest voices are listed per guest.'), '',
           (L['style']), C['style'], '', (L['open'])]
    L_ += [f'> **{w}**：{t.replace("{X}", "[X]")}' for w, t in C['opening_lines']]
    if lang == 'zh':
        L_ += ['', L['head'],
               '> 播客间空镜无人 → 主持人从左侧入座 → 嘉宾已坐在右侧等待。所有篇共用，建立辨识度。']
    else:
        L_ += ['', L['head'],
               '> Empty studio → host enters from the left and sits → guest is already seated on the right. '
               'Shared by every episode to build recognition.']
    L_ += ['', '---', '']

    for gi, g in enumerate(guest_list(lang), 1):
        L_ += [f'## {gi}. {g["name"]}', '', L['persona'], g['persona'], '',
               L['manner'], g['manner'], '', L['guest_voice'], g['voice'], '']
        for qi, q in enumerate(g['q'], 1):
            L_ += [(f'{L["q"]}{qi} · {q["t"]}**' if lang == 'en' else f'{L["q"]}{qi} · {q["t"]}**'), '']
            L_ += [f'> **{w}**：{t}' for w, t in q['lines']]
            L_ += ['']
        e = g['ending']
        L_ += [f'**{e["t"]}**', '']
        L_ += [f'> **{w}**：{t}' for w, t in e['lines']]
        L_ += ['', '---', '']

    L_ += [L['make'], '']
    if lang == 'zh':
        L_ += ['**逐段生成**：每段单独跑一次视频模型（5~10s），用主持人照片作**角色参考图**，'
               '嘉宾用各自形象卡作参考，保证各段人物不变脸。', '',
               '**台词留白**：回答之间留 1~2 秒静默，这是"思想感"的来源，别让模型一口气念完。', '',
               '**配音**：主持人用自己的声音最好；嘉宾按形象卡的声音设定，语速压到 0.8 倍。', '',
               '**剪辑**：段间不加转场（固定机位直接切，反而像真实播客）；底部加极简字幕。', '',
               '**片尾挂链**（导流到思想会客厅）：', '']
    else:
        L_ += ["**Generate segment by segment**: run the video model once per segment (5~10s). Use a photo of the "
               "host as the **character reference**, and each guest's character card as their reference, so faces "
               "stay consistent across segments.", '',
               "**Leave silence**: 1~2 seconds between lines — that silence is where the weight comes from. "
               "Don't let the model rush through it.", '',
               "**Voice**: the host is best voiced by yourself; cast each guest from their voice description and "
               "slow the delivery to about 0.8x.", '',
               "**Edit**: no transitions between segments (hard cuts on a locked-off camera read as a real podcast); "
               "add minimal subtitles at the bottom.", '',
               "**Closing card** (drives traffic to the salon):", '']
    L_ += [L['link'], L['table']]
    for g in guest_list(lang):
        L_.append(f'| {g["name"]} | `{ZH.LANDING}/?thinker={g["id"]}` |')
    L_ += ['', ('片尾统一叠一行小字：`与[X]继续聊 →`，与该人物的卡片/海报二维码形成闭环。' if lang == 'zh'
                else 'Use one consistent closing caption: `Keep talking with [X] →`, paired with that thinker\'s '
                     'card/poster QR code.')]
    open(md, 'w', encoding='utf-8').write('\n'.join(L_))
    return md


def main():
    args = sys.argv[1:]
    lang = 'both'
    if '--lang' in args:
        i = args.index('--lang')
        lang = args[i + 1] if i + 1 < len(args) else 'both'
    only_md = '--md-only' in args
    only_p = '--prompts-only' in args
    wanted = None
    if '--guest' in args:
        i = args.index('--guest')
        wanted = set(args[i + 1:i + 1 + (len(args) - i - 1)])

    langs = ['zh', 'en'] if lang == 'both' else [lang]
    total = 0
    for lg in langs:
        targets = [g for g in guest_list(lg) if not wanted or g['id'] in wanted]
        if not only_md:
            for g in targets:
                fs = write_prompts(lg, g)
                total += len(fs)
                print(f'  [{lg}] {g["name"]:14s} -> {"prompts" if lg=="zh" else "prompts-en"}/{g["id"]}/ ({len(fs)} files)')
        if not only_p:
            print(f'  [{lg}] doc -> {build_md(lg)}')
    print(f'done: {len(langs)} language(s), {total} prompt files')


if __name__ == '__main__':
    main()
