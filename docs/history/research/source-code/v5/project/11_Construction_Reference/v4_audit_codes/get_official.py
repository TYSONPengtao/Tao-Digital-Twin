import re,urllib.request,json
from pathlib import Path
pages={'55038':'https://szwb.sz.gov.cn/gwszwfw/zsk/hybz/content/post_12543586.html','55030':'https://szwb.sz.gov.cn/gwszwfw/zsk/hybz/content/post_10187002.html','55032':'https://www.hunan.gov.cn/zqt/zcsd/202208/t20220825_27756285.html','55031':'https://zjj.sm.gov.cn/xxgk/fgwj/jsbz/202209/t20220909_1827378.htm'}
for k,u in pages.items():
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
  raw=urllib.request.urlopen(req,timeout=15).read().decode('utf-8','replace')
  links=[urllib.parse.urljoin(u,x) for x in re.findall(r'(?:href|src)=[\"\']([^\"\']+\.(?:pdf|PDF)(?:\?[^\"\']*)?)[\"\']',raw)]
  Path('work/v4_audit_codes/'+k+'_page.html').write_text(raw,encoding='utf-8'); print(k,json.dumps(links,ensure_ascii=False))
  for i,l in enumerate(links):
   try:
    data=urllib.request.urlopen(urllib.request.Request(l,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
    if data.startswith(b'%PDF'):Path('work/v4_audit_codes/'+k+'_full_'+str(i)+'.pdf').write_bytes(data);print('SUCCESS',k,len(data),l)
   except Exception as e:print('FAILPDF',str(e))
 except Exception as e:print('FAIL',k,str(e))
