import sys,re,html
x=open(sys.argv[1],encoding='utf-8',errors='replace').read()
m=re.search(r'<main.*?</main>',x,re.S) or re.search(r'<div id="tmp_contents".*?<div id="tmp_footer',x,re.S)
x=m.group(0) if m else x
x=re.sub(r'<(script|style).*?</\1>','',x,flags=re.S); x=re.sub(r'<(br|/p|/li|/tr|/h\d|/dd|/dt)[^>]*>','\n',x); x=re.sub(r'<[^>]+>','',x)
x=html.unescape(x); x=re.sub(r'[ \t　]+',' ',x); x=re.sub(r'\n\s*\n+','\n',x)
print(x.strip())
