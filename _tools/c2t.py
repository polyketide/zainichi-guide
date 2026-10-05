import sys, re, html
# 把政府网站页面转成纯文本（去脚本、样式、标签）。
# 编码按页面里的 charset 声明读：中国政府网站多为 utf-8，日本国税厅是 Shift_JIS。
raw = open(sys.argv[1], 'rb').read()
m = re.search(rb'charset=["\']?([A-Za-z0-9_\-]+)', raw[:4000])
enc = m.group(1).decode('ascii').lower() if m else 'utf-8'
if enc in ('shift_jis', 'shift-jis', 'sjis', 'x-sjis'):
    enc = 'cp932'
x = raw.decode(enc, errors='replace')
x = re.sub(r'<(script|style).*?</\1>', '', x, flags=re.S)
x = re.sub(r'<(br|/p|/div|/li|/tr|/h\d|/dd|/dt)[^>]*>', '\n', x)
x = re.sub(r'<[^>]+>', '', x)
x = html.unescape(x)
x = re.sub(r'[ \t　\xa0]+', ' ', x)
x = re.sub(r'\n\s*\n+', '\n', x)
print(x.strip())
