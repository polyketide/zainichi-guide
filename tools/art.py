import sys,re
import xml.etree.ElementTree as ET
# 用法: art.py <法令.xml> <条号>...   条号写 19_9；原始附則的条写 S:137
f=sys.argv[1]; nums=sys.argv[2:]
root=ET.parse(f).getroot()
main=root.find('.//MainProvision')
suppl=[s for s in root.iter('SupplProvision') if not s.get('AmendLawNum')]
def txt(e): return re.sub(r'\s+','',''.join(e.itertext())) if e is not None else ''
def show(a,tag):
    print('##',tag,txt(a.find('ArticleCaption')))
    for p in a.findall('Paragraph'):
        print(' P'+p.get('Num'),txt(p.find('ParagraphSentence'))[:int(__import__("os").environ.get("W","900"))])
        for i in p.findall('Item'):
            print('   -',txt(i.find('ItemTitle')),txt(i.find('ItemSentence'))[:400])
        for t in p.iter('TableRow'):
            print('   |',' | '.join(txt(c) for c in t.findall('TableColumn')))
for a in main.iter('Article'):
    if a.get('Num') in nums: show(a,a.get('Num'))
for s in suppl:
    for a in s.iter('Article'):
        if 'S:'+a.get('Num') in nums: show(a,'附則'+a.get('Num'))
