import json,os,sys,urllib.request
E=999999;V={112:1,110:3,98:3,114:5,113:9,107:0};tt={};bn=0
D=((1,-1),(1,1),(-1,-1),(-1,1),(1,0),(-1,0),(0,1),(0,-1))
KN=((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
def gb(fen):
 b={};r=7;f=0
 for c in fen.split(' ')[0]:
  if c=='/':r-=1;f=0
  elif c.isdigit():f+=int(c)
  else:b[f+r*8]=c;f+=1
 return b
def mv(fr,to,pp,cap):return (fr<<24)|(to<<16)|(pp<<8)|cap
def gen(b,t):
 m=[]
 for k in b:
  p=b[k];isw=p.isupper()
  if (isw)!=(t==0):continue
  fr=k;f=fr%8;r=fr//8
  if p.lower()=='p':
   nr=r+(1 if t==0 else -1)
   if 0<=nr<8 and nr*8+f not in b:
    if nr in (0,7):
     for pp in (113,114,98,110):m.append(mv(fr,nr*8+f,pp,0))
    else:m.append(mv(fr,nr*8+f,0,0))
   for df in (-1,1):
    nk=nr*8+f+df
    if 0<=f+df<8 and 0<=nr<8 and nk in b and b[nk].isupper()!=isw:m.append(mv(fr,nk,113 if nr in (0,7) else 0,V[ord(b[nk].lower())]))
  elif p.lower()=='n':
   for dr,df in KN:
    nr,nc=r+dr,f+df
    if 0<=nr<8 and 0<=nc<8:
     nk=nr*8+nc;q=b.get(nk)
     if not q or q.isupper()!=isw:m.append(mv(fr,nk,0,V[ord(q.lower())] if q else 0))
  elif p.lower() in 'bqrk':
   ds=D if p.lower()=='k' else ((1,-1),(1,1),(-1,-1),(-1,1)) if p.lower()=='b' else ((1,0),(-1,0),(0,1),(0,-1)) if p.lower()=='r' else D
   for dr,df in ds:
    nr,nc=r,f
    for _ in range(1 if p.lower()=='k' else 7):
     nr+=dr;nc+=df
     if not(0<=nr<8 and 0<=nc<8):break
     nk=nr*8+nc;q=b.get(nk)
     if not q:m.append(mv(fr,nk,0,0))
     else:
      if q.isupper()!=isw:m.append(mv(fr,nk,0,V[ord(q.lower())]))
      break
 return m
def ev(b,t):
 sc=0
 for k,p in b.items():
  v=V[ord(p.lower())]
  if p.isupper()==(t==0):sc+=v
  else:sc-=v
 return sc
def ab(b,d,a,b2,t):
 global bn;bn+=1
 if d<=0:return ev(b,t)
 be=-E
 for mv in gen(b,t):
  fr=(mv>>24)&63;to=(mv>>16)&63;pp=(mv>>8)&255
  p=b.get(fr);del b[fr];b[to]=chr(pp) if pp else p
  val=-ab(b,d-1,-b2,-a,1-t)
  if pp:del b[to]
  else:b[to]=p
  b[fr]=p
  if val>be:be=val
  if be>=b2:break
  if be>a:a=be
 return be
ENV=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("no ENV")
def post(p,body):
 r=urllib.request.Request(ENV+p,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
 try:
  with urllib.request.urlopen(r) as res:return json.load(res)
 except urllib.error.HTTPError as e:sys.exit(f"{p}:{e.code}")
while True:
 g=post("/game",{})
 if g["status"]=="done":break
 while g["status"]=="your_move":
  b=gb(g["fen"]);ms=g["legal_moves"];be=-E;bm=None
  for m in ms:
   fr=ord(m[0])-97+(8-int(m[1]))*8;to=ord(m[2])-97+(8-int(m[3]))*8
   pp=ord(m[4]) if len(m)==5 else 0;capv=V.get(pp,0) if pp else 0
   mvk=mv(fr,to,pp,capv);p=b.get(fr);del b[fr];b[to]=chr(pp) if pp else p
   sc=-ab(b,2,-E,E,1 if g["colour"]=="white" else 0)
   if pp:del b[to]
   else:b[to]=p
   b[fr]=p
   if sc>be:be=sc;bm=mvk
  if bm:
   fr=(bm>>24)&63;to=(bm>>16)&63;pp=(bm>>8)&255
   m=chr(97+fr%8)+str(8-fr//8)+chr(97+to%8)+str(8-to//8)+(chr(pp) if pp else '')
   g=post("/move",{"game":g["game"],"move":m})
print("done",file=sys.stderr)
