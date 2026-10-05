import sys,re,html
# 把中国政府网站页面转成纯文本（去脚本、样式、标签）
x=open(sys.argv[1],encoding='utf-8',errors='replace').read()
x=re.sub(r'<(script|style).*?</\1>','',x,flags=re.S); x=re.sub(r'<(br|/p|/div|/li|/tr|/h\d)[^>]*>','\n',x); x=re.sub(r'<[^>]+>','',x)
x=html.unescape(x); x=re.sub(r'[ \t　\xa0]+',' ',x); x=re.sub(r'\n\s*\n+','\n',x); print(x.strip())
