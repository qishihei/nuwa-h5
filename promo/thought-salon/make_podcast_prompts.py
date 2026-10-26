#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""播客访谈视频 · 生成流水线

从 podcast_data.py（单一数据源）生成：
  1) 逐段提示词文件  podcast-prompts/<guest-id>/NN-<段名>.txt   ← 直接复制喂视频模型
  2) 合并文档        podcast-scripts.md                          ← 人类阅读 / 存档

用法:
    python3 make_podcast_prompts.py              # 全部生成
    python3 make_podcast_prompts.py --md-only    # 只更新 md
    python3 make_podcast_prompts.py --prompts-only
    python3 make_podcast_prompts.py --guest confucius laozi    # 只生成指定嘉宾
"""

import os
import re
import sys

from podcast_data import COMMON, GUESTS, LANDING

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'prompts')
MD = os.path.join(HERE, 'podcast-scripts.md')


def safe(name: str) -> str:
    """文件名安全化：去掉 / 空格标点，保留中英文数字与连字符。"""
    s = re.sub(r'[\\/:*?"<>|\s]+', '-', name)
    return re.sub(r'-+', '-', s).strip('-') or 'seg'


def seg_prompt(g, idx, title, stage, lines, dur):
    """生成单段提示词文本（可直接喂视频模型）。"""
    name = g['name']
    out = [
        f'写实播客访谈视频，16:9 横屏，专业电影摄影机拍摄，固定机位中景，两人同框，画面稳定。约 {dur} 秒。',
        '',
        f'【环境】{COMMON["env"]}',
        '',
        f'【主持人（画面左侧）】{COMMON["host"]}',
        '',
        f'【嘉宾：{name}（画面右侧）】{g["persona"]}',
        f'说话方式：{g["manner"]}',
        '',
        f'【镜头与表演】{COMMON["camera"]}',
        f'本段具体要求：{stage}',
        '',
        '【台词】',
    ]
    for who, line in lines:
        out.append(f'{who}：{line}')
    out += [
        '',
        f'【声音】{COMMON["host_voice"]} {g["voice"]}',
        f'【风格】{COMMON["style"]}',
        '',
        '注意：台词之间保留 1~2 秒静默停顿，不要一口气念完；人物在整段中保持不动，仅头部与手部有细微动作。',
    ]
    return '\n'.join(out)


def head_prompt(g):
    return '\n'.join([
        '写实播客访谈视频，16:9 横屏，专业电影摄影机拍摄，固定机位中景，约 3 秒。',
        '',
        f'【环境】{COMMON["env"]}',
        '',
        '【画面内容】开场空镜：播客间内暂时无人，两把皮椅与中间小边几上的两杯清水入镜，'
        '书架灯带暖光稳定，画面完全静止。随后主持人从左侧入座，嘉宾已坐在右侧等待。'
        '无人物特写、无运镜，只是一次安静的落座。',
        '',
        f'【风格】{COMMON["style"]}',
        '',
        '（本段为系列统一片头，所有嘉宾共用，用于建立节目辨识度）',
    ])


def write_prompts(g):
    d = os.path.join(OUT, g['id'])
    os.makedirs(d, exist_ok=True)
    files = []

    # 00 片头
    p = os.path.join(d, '00-片头.txt')
    open(p, 'w', encoding='utf-8').write(head_prompt(g))
    files.append(p)

    # 01 开场
    lines = [(w, t.replace('{X}', g['name'])) for w, t in COMMON['opening_lines']]
    p = os.path.join(d, '01-开场.txt')
    open(p, 'w', encoding='utf-8').write(
        seg_prompt(g, 1, '开场', COMMON['opening_stage'], lines, COMMON['opening_dur']))
    files.append(p)

    # 02~05 四轮问答
    for i, q in enumerate(g['q'], start=2):
        p = os.path.join(d, f'{i:02d}-{safe(q["t"])}.txt')
        open(p, 'w', encoding='utf-8').write(seg_prompt(g, i, q['t'], q['stage'], q['lines'], 14))
        files.append(p)

    # 06 收尾
    e = g['ending']
    p = os.path.join(d, f'{len(g["q"]) + 2:02d}-{safe(e["t"])}.txt')
    open(p, 'w', encoding='utf-8').write(
        seg_prompt(g, len(g['q']) + 2, e['t'], e['stage'], e['lines'], e.get('dur', 13)))
    files.append(p)

    # 合并文件
    merged = []
    for f in files:
        merged.append(open(f, encoding='utf-8').read())
    mp = os.path.join(d, f'ALL-{safe(g["name"])}.md')
    open(mp, 'w', encoding='utf-8').write(
        f'# {g["name"]} · 播客访谈视频 全段提示词\n\n' + '\n\n---\n\n'.join(merged))
    return files + [mp]


def build_md():
    L = [f'# {COMMON["title"]}', '',
         '> 本文件由 `make_podcast_prompts.py` 从 `podcast_data.py` 自动生成，请勿手改。',
         '> 改数据后重新运行脚本即可。', '',
         '同一档节目：**同一个播客间、同一个机位、同一位主持人（我）、换不同嘉宾**。',
         '用于 AI 视频逐段生成（5~10s 一段）后拼接，片尾挂思想会客厅深链导流。', '',
         '---', '', '## 通用设定（所有篇共用）', '',
         '**环境**', COMMON['env'], '',
         '**机位与表演**', COMMON['camera'], '',
         '**主持人（"我"，左边人物）**', COMMON['host'], '',
         '**声音**', COMMON['host_voice'], '嘉宾声音见各篇。', '',
         '**风格与输出**', COMMON['style'], '',
         '**开场句（复用）**']
    for w, t in COMMON['opening_lines']:
        L.append(f'> **{w}**：{t.replace("{X}", "[X]")}')
    L += ['', '**片头（3 秒，系列统一）**',
          '> 播客间空镜无人 → 主持人从左侧入座 → 嘉宾已坐在右侧等待。所有篇共用，建立辨识度。', '', '---', '']

    for gi, g in enumerate(GUESTS, 1):
        L += [f'## {gi}. {g["name"]}', '',
              f'**形象卡**：{g["persona"]}', '',
              f'**说话方式**：{g["manner"]}', '',
              f'**声音**：{g["voice"]}', '']
        for qi, q in enumerate(g['q'], 1):
            L += [f'**问{qi} · {q["t"]}**', '']
            L += [f'> **{w}**：{t}' for w, t in q['lines']]
            L += ['']
        e = g['ending']
        L += [f'**{e["t"]}**', '']
        L += [f'> **{w}**：{t}' for w, t in e['lines']]
        L += ['', '---', '']

    L += ['## 制作与投放', '',
          '**逐段生成**：每段单独跑一次视频模型（5~10s），用主持人照片作**角色参考图**，'
          '嘉宾用各自形象卡作参考，保证各段人物不变脸。', '',
          '**台词留白**：回答之间留 1~2 秒静默，这是"思想感"的来源，别让模型一口气念完。', '',
          '**配音**：主持人用自己的声音最好；嘉宾按形象卡的声音设定，语速压到 0.8 倍。', '',
          '**剪辑**：段间不加转场（固定机位直接切，反而像真实播客）；底部加极简字幕。', '',
          '**片尾挂链**（导流到思想会客厅）：', '', '| 嘉宾 | 深链 |', '|---|---|']
    for g in GUESTS:
        L.append(f'| {g["name"]} | `{LANDING}/?thinker={g["id"]}` |')
    L += ['', '片尾统一叠一行小字：`与[X]继续聊 →`，与该人物的卡片/海报二维码形成闭环。', '']
    open(MD, 'w', encoding='utf-8').write('\n'.join(L))
    return MD


def main():
    args = sys.argv[1:]
    only_md = '--md-only' in args
    only_p = '--prompts-only' in args
    wanted = None
    if '--guest' in args:
        i = args.index('--guest')
        wanted = set(args[i + 1:i + 1 + (len(args) - i - 1)])

    targets = [g for g in GUESTS if not wanted or g['id'] in wanted]
    total = 0
    if not only_md:
        for g in targets:
            fs = write_prompts(g)
            total += len(fs)
            print(f'  {g["name"]:12s} -> prompts/{g["id"]}/  ({len(fs)} 个文件)')
    if not only_p:
        md = build_md()
        print(f'  文档 -> {md}')
    print(f'完成：{len(targets)} 位嘉宾，生成 {total} 个提示词文件')


if __name__ == '__main__':
    main()
