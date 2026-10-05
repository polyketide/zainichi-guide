#!/usr/bin/env python3
"""检查正文的结构和交叉引用。用法: python3 tools/check.py [--stats]
- 每条必须有: 标题、成本标签注释、成本/说人话/收益/证据等级/来源/备注 六栏（译本用各自的栏名）。
- 中文正本里的「第 X 节第 Y 条（锚点）」「第 Y 条（锚点）」必须指向存在的条目，锚点里要有连续两个字出现在目标标题里。
- 译本（ja/ en/）每节的条数、每条的成本标签、证据等级必须和中文正本一致。
"""
import re, sys, glob, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = {
    'zh': ['成本', '说人话', '收益', '证据等级', '来源', '备注'],
    'ja': ['コスト', 'ひとことで', '根拠', '証拠レベル', '出典', '備考'],
    'en': ['Cost', 'In plain words', 'Benefit', 'Evidence', 'Sources', 'Notes'],
}
DIRS = {'zh': 'book', 'ja': 'ja/book', 'en': 'en/book'}
TAG = re.compile(r'<!-- 成本标签: 钱=(0|少|多) 时间=(少|中|多) 毅力=(否|些|是) 收益=(大|中|小) 口径=(死亡率|金钱|时间|自由) -->')

def parse(lang):
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, DIRS[lang], '[0-9][0-9]-*.md'))):
        sec = int(os.path.basename(f)[:2]); txt = open(f, encoding='utf-8').read()
        ents = []
        for m in re.finditer(r'(?m)^### (\d+)\. (.+)\n((?:(?!^### ).*\n?)*)', txt):
            body = m.group(3); tag = TAG.search(body)
            fl = {k: re.search(r'(?m)^- ' + re.escape(k) + r'[：:]\s*(.*)$', body) for k in FIELDS[lang]}
            ents.append({'n': int(m.group(1)), 'title': m.group(2).strip(), 'tag': tag.group(0) if tag else None,
                         'fields': {k: (v.group(1) if v else None) for k, v in fl.items()}, 'body': body})
        out[sec] = {'file': f, 'text': txt, 'entries': ents}
    return out

def main():
    errs = []; zh = parse('zh')
    for sec, d in zh.items():
        for i, e in enumerate(d['entries'], 1):
            where = f'zh 第{sec}节第{e["n"]}条'
            if e['n'] != i: errs.append(f'{where}: 条号不连续')
            if not e['tag']: errs.append(f'{where}: 缺成本标签')
            for k, v in e['fields'].items():
                if not v: errs.append(f'{where}: 缺「{k}」栏')
            lv = (e['fields']['证据等级'] or '')[:1]
            if lv not in 'ABC' or not lv: errs.append(f'{where}: 证据等级不是 A/B/C')
    # 交叉引用
    nref = 0
    for sec, d in zh.items():
        for m in re.finditer(r'(?:见|看|按)?(?:本节)?(?:第 (\d+) 节)?第 (\d+) 条（([^）]+)）', d['text']):
            s = int(m.group(1)) if m.group(1) else sec; n = int(m.group(2)); anchor = m.group(3)
            pre = d['text'][max(0, m.start() - 12):m.start()]
            if not m.group(1) and re.search(r'([法令则定典》]|违反)\s*$', pre): continue  # 法条条号，不是条目引用
            nref += 1
            tgt = next((e for e in zh.get(s, {'entries': []})['entries'] if e['n'] == n), None)
            if not tgt: errs.append(f'zh 第{sec}节: 引用 第{s}节第{n}条 不存在（{anchor}）'); continue
            if not any(anchor[i:i + 2] in tgt['title'] for i in range(len(anchor) - 1)):
                errs.append(f'zh 第{sec}节: 引用 第{s}节第{n}条（{anchor}）与标题对不上 → {tgt["title"]}')
    # 译本对齐
    for lang in ('ja', 'en'):
        tr = parse(lang)
        if not tr: continue
        for sec, d in zh.items():
            if sec not in tr: errs.append(f'{lang}: 缺第{sec}节'); continue
            a, b = d['entries'], tr[sec]['entries']
            if len(a) != len(b): errs.append(f'{lang} 第{sec}节: 条数 {len(b)} ≠ 正本 {len(a)}'); continue
            for x, y in zip(a, b):
                w = f'{lang} 第{sec}节第{x["n"]}条'
                if x['tag'] != y['tag']: errs.append(f'{w}: 成本标签与正本不同')
                for k, v in y['fields'].items():
                    if not v: errs.append(f'{w}: 缺「{k}」栏')
                lv_key = FIELDS[lang][3]
                if (y['fields'][lv_key] or '')[:1] != (x['fields']['证据等级'] or '')[:1]: errs.append(f'{w}: 证据等级与正本不同')
                za = set(re.findall(r'https?://[^\s>）)]+', x['fields']['来源'] or '')); tb = set(re.findall(r'https?://[^\s>）)]+', y['fields'][FIELDS[lang][4]] or ''))
                if za != tb: errs.append(f'{w}: 来源栏的链接与正本不同')
    total = sum(len(d['entries']) for d in zh.values())
    lv = {k: sum(1 for d in zh.values() for e in d['entries'] if (e['fields']['证据等级'] or '').startswith(k)) for k in 'ABC'}
    links = sum(len(re.findall(r'https?://', e['fields']['来源'] or '')) for d in zh.values() for e in d['entries'])
    stats = {'sections': len(zh), 'entries': total, 'A': lv['A'], 'B': lv['B'], 'C': lv['C'], 'source_links': links, 'xrefs': nref,
             'per_section': {s: len(d['entries']) for s, d in zh.items()}}
    if '--stats' in sys.argv: print(json.dumps(stats, ensure_ascii=False))
    else: print(f'{stats["sections"]} 节 {total} 条（A {lv["A"]} / B {lv["B"]} / C {lv["C"]}），来源链接 {links} 处，条目引用 {nref} 处')
    for e in errs: print('✗', e)
    print('通过' if not errs else f'{len(errs)} 处问题'); sys.exit(1 if errs else 0)
main()
