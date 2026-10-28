import random
from PIL import Image
from asm2 import BASE
PAL=['1a1c2c','5d275d','b13e53','ef7d57','ffcd75','a7f070','38b764','257179','29366f','3b5dc9','41a6f6','73eff7','f4f4f4','94b0c2','566c86','333c57']
class CPU:
    def __init__(s, code, seed=1):
        random.seed(seed)
        s.mem=[0]*8192
        for i,b in enumerate(code): s.mem[BASE+i]=b
        s.regs=[0]*4; s.pc=BASE; s.sp=8180
        s.instr=0; s.frames=0; s.inframe=0; s.sounds=[]
        s.minsp=8180; s.codeend=BASE+len(code); s.bad=[]
        s.written=set()
    def push(s,v):
        s.sp-=1; s.mem[s.sp]=v%256
        s.minsp=min(s.minsp,s.sp)
    def pop(s):
        v=s.mem[s.sp]; s.sp+=1; return v
    def wr(s,a,v):
        if not (0<=a<8192): s.bad.append(('oob',a)); return
        if BASE<=a<s.codeend and a not in s.selfmod: s.bad.append(('codewrite',a,s.pc))
        s.mem[a]=v%256
    selfmod=set()
    def step(s):
        m=s.mem; r=s.regs
        op,a1,a2=m[s.pc],m[s.pc+1],m[s.pc+2]; pc0=s.pc; s.pc+=3; s.instr+=1; s.inframe+=1; g=op>>4
        if op==0: raise Exception('HALT')
        elif op==1: s.frames+=1; s.inframe=0
        elif op==2: s.sounds.append((s.frames,a1,a2))
        elif op==3: r[a1]=random.randint(0,a2)
        elif op==0x10: r[a1]=a2
        elif op==0x11: r[a1]=r[a2]
        elif op==0x12: r[a1]=m[r[2]*256+r[3]] if r[2]*256+r[3]<8192 else 0
        elif op==0x13: s.wr(r[2]*256+r[3], r[a1])
        elif g in (2,3):
            l=r[a1]; rr=r[a2] if g==2 else a2; k=op&15
            r[a1]=[(l+rr)%256,(l-rr)%256,(l*rr)%256,l&rr,l^rr][k]
        elif op==0x40: s.pc=a1*256+a2
        elif op==0x41:
            if r[a1]==r[a2]: s.pc+=3
        elif op==0x42:
            if r[a1]!=r[a2]: s.pc+=3
        elif op==0x43:
            if r[a1]<r[a2]: s.pc+=3
        elif op==0x44: s.push(s.pc%256); s.push(s.pc//256); s.pc=a1*256+a2
        elif op==0x45: hi=s.pop(); s.pc=hi*256+s.pop()
        elif op==0x46: s.push(r[a1])
        elif op==0x47: r[a1]=s.pop()
        elif op==0x50:
            a=r[1]*64+r[0]
            if a>=8192: s.bad.append(('getpx',a)); r[a1]=0
            else: r[a1]=m[a]%16
        elif op==0x51:
            a=r[1]*64+r[0]
            if a>=4096: s.bad.append(('setpx-oob',r[0],r[1],pc0))
            else: m[a]=r[a1]%256
        elif op==0x52:
            direction=a1
            if direction==0:
                for y in range(63):
                    m[y*64:(y+1)*64]=m[(y+1)*64:(y+2)*64]
                m[4032:4096]=[0]*64
            elif direction==1:
                for y in range(63, 0, -1):
                    m[y*64:(y+1)*64]=m[(y-1)*64:y*64]
                m[:64]=[0]*64
            elif direction==2:
                for y in range(64):
                    row=y*64
                    for x in range(63): m[row+x]=m[row+x+1]
                    m[row+63]=0
            elif direction==3:
                for y in range(64):
                    row=y*64
                    for x in range(63, 0, -1): m[row+x]=m[row+x-1]
                    m[row]=0
        elif op==0x54:
            block=[]
            for y in range(a2):
                for x in range(a1):
                    sx=r[0]+x; sy=r[1]+y
                    block.append(m[sy*64+sx] if 0<=sx<64 and 0<=sy<64 else 0)
            for y in range(a2):
                for x in range(a1):
                    dx=r[2]+x; dy=r[3]+y
                    if 0<=dx<64 and 0<=dy<64: m[dy*64+dx]=block[y*a1+x]
        elif op==0x53:
            for i in range(4096): m[i]=r[a1]%16
        else: raise Exception(f'bad op {op:02x} at {pc0}')
        if s.inframe>=100: s.frames+=1; s.inframe=0
    def run(s, maxinstr, snaps=None, stop=None):
        snaps=snaps or {}
        while s.instr<maxinstr:
            s.step()
            if s.instr in snaps: s.snap(snaps[s.instr])
            if stop and stop(s): break
    def snap(s, name, S=8):
        img=Image.new('RGB',(64*S,64*S)); px=img.load()
        for y in range(64):
            for x in range(64):
                c=PAL[s.mem[y*64+x]%16]; rgb=tuple(int(c[i:i+2],16) for i in (0,2,4))
                for dy in range(S):
                    for dx in range(S): px[x*S+dx,y*S+dy]=rgb
        img.save(name)
