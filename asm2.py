OPS = dict(HALT=0x00,WAIT=0x01,SOUND=0x02,RND=0x03,LOAD=0x10,MOVE=0x11,LDM=0x12,STM=0x13,
 ADD=0x20,SUB=0x21,MUL=0x22,AND=0x23,XOR=0x24,ADDV=0x30,SUBV=0x31,MULV=0x32,ANDV=0x33,XORV=0x34,
 JMP=0x40,SKEQ=0x41,SKNE=0x42,SKLT=0x43,CALL=0x44,RET=0x45,PUSH=0x46,POP=0x47,
 GETPX=0x50,SETPX=0x51,SCROLL=0x52,FILL=0x53,COPYBLOCK=0x54)
REG = dict(A=0,B=1,C=2,D=3)
BASE = 4096
class Prog:
    def __init__(s):
        s.items=[]; s.labels={}; s.nreg=[None]*4
    def addr(s): return BASE+3*len(s.items)
    def label(s, name):
        assert name not in s.labels, name
        s.labels[name]=s.addr(); s.nreg=[None]*4
    def ins(s, m, a1=0, a2=0):
        s.items.append((m,a1,a2))
    def nop(s): s.ins('MOVE','A','A')
    def align_fit(s, nbytes):
        while (s.addr()%256)+nbytes>256: s.nop()
    def load(s, r, v):
        if isinstance(v,int) and s.nreg[REG[r]]==v: return
        s.ins('LOAD', r, v)
        s.nreg[REG[r]] = v if isinstance(v,int) else None
    def forget(s): s.nreg=[None]*4
    def link(s):
        code=[]
        def res(x):
            if isinstance(x,str) and x in REG: return REG[x]
            if callable(x): return x(s.labels)
            return x
        for m,a1,a2 in s.items:
            if isinstance(a1,tuple) and a1[0]=='L':
                t=s.labels[a1[1]]+(a1[2] if len(a1)>2 else 0); b1,b2=t//256,t%256
            else:
                b1,b2=res(a1),res(a2)
            assert 0<=b1<256 and 0<=b2<256,(m,a1,a2,b1,b2)
            code+=[OPS[m],b1,b2]
        return code
def L(name,off=0): return ('L',name,off)
def pg(name,k=0):
    return lambda sym: (sym[name]+k)//256
def of(name,k=0):
    return lambda sym: (sym[name]+k)%256
def dis(code):
    inv={v:k for k,v in OPS.items()}
    out=[]
    for i in range(0,len(code),3):
        out.append((BASE+i,inv.get(code[i],'?%02x'%code[i]),code[i+1],code[i+2]))
    return out
