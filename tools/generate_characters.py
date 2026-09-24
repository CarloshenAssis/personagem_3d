#!/usr/bin/env python3
"""Build the Armed Mystery low-poly character pack without external dependencies.

The script is the editable procedural source: it writes self-contained glTF 2.0
binary files and software-rendered PNG previews using only Python's stdlib.
"""
from __future__ import annotations

import json, math, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models"
PRE = ROOT / "previews"

VARIANTS = {
    "ember": {"jacket":"#30363E", "pants":"#343B31", "skin":"#B88E72", "hair":"#3B2A20", "accent":"#B48A55", "detail":"shoulder_band", "hair_style":"left"},
    "moss":  {"jacket":"#39433B", "pants":"#292D32", "skin":"#8E624D", "hair":"#171616", "accent":"#87936D", "detail":"back_yoke", "hair_style":"right"},
    "dawn":  {"jacket":"#51443F", "pants":"#343A40", "skin":"#D0A184", "hair":"#6A4631", "accent":"#C19B78", "detail":"sleeve_cuffs", "hair_style":"fringe"},
    "night": {"jacket":"#292D38", "pants":"#3C3933", "skin":"#704B3D", "hair":"#242126", "accent":"#77728A", "detail":"hem_band", "hair_style":"left"},
    "cedar": {"jacket":"#4A4035", "pants":"#30372F", "skin":"#A8755C", "hair":"#2C2019", "accent":"#8F8068", "detail":"chest_panel", "hair_style":"right"},
    "ash":   {"jacket":"#44484A", "pants":"#36353A", "skin":"#C49376", "hair":"#AAA096", "accent":"#8B9092", "detail":"knee_panels", "hair_style":"crop"},
    "sand":  {"jacket":"#625B49", "pants":"#3D4037", "skin":"#6F4938", "hair":"#161514", "accent":"#A69B78", "detail":"double_back", "hair_style":"fringe"},
    "plum":  {"jacket":"#453B49", "pants":"#33383A", "skin":"#D2AA8D", "hair":"#51382D", "accent":"#8E788F", "detail":"side_panels", "hair_style":"crop"},
}
COMMON = {"shoe":"#131518", "metal":"#525960", "eye":"#17191B"}

def rgb(h):
    h=h.lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]+[1]

def norm(v):
    q=math.sqrt(sum(x*x for x in v)) or 1; return tuple(x/q for x in v)

def mesh(): return {"v":[],"n":[],"i":[],"parts":[]}

def add_poly(m, verts, faces, mat, name):
    start=len(m["i"]); base=len(m["v"])
    # Flat shading: each triangle gets independent vertices.
    for f in faces:
        a,b,c=(verts[x] for x in f)
        no=norm(((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),
                 (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),
                 (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])))
        for p in (a,b,c): m["v"].append(p); m["n"].append(no); m["i"].append(len(m["i"]))
    m["parts"].append((name,mat,start,len(m["i"])-start))

def box(m, name, center, size, mat, bevel=0):
    x,y,z=center; sx,sy,sz=(q/2 for q in size)
    v=[(x+a*sx,y+b*sy,z+c*sz) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5)]
    add_poly(m,v,f,mat,name)

def frustum(m,name,center,bottom,top,height,depth,mat,segments=8):
    cx,cy,cz=center; v=[]
    for yy,w in ((cy-height/2,bottom),(cy+height/2,top)):
        for k in range(segments):
            a=2*math.pi*k/segments; v.append((cx+math.cos(a)*w/2,yy,cz+math.sin(a)*depth/2))
    v += [(cx,cy-height/2,cz),(cx,cy+height/2,cz)]
    f=[]
    for k in range(segments):
        j=(k+1)%segments; f += [(k,j,segments+j),(k,segments+j,segments+k),(2*segments,j,k),(2*segments+1,segments+k,segments+j)]
    add_poly(m,v,f,mat,name)

def build(cfg):
    m=mesh(); J="jacket"; P="pants"; S="skin"; H="hair"; A="accent"
    # soles 0.00..0.08, shoes point toward +Z
    box(m,"Shoe.L",(-.105,.045,.035),(.18,.09,.38),"shoe"); box(m,"Shoe.R",(.105,.045,.035),(.18,.09,.38),"shoe")
    # legs, knees exactly at 0.50, crotch at 0.92
    frustum(m,"Shin.L",(-.105,.29,0),.145,.17,.42,.16,P); frustum(m,"Shin.R",(.105,.29,0),.145,.17,.42,.16,P)
    frustum(m,"Thigh.L",(-.105,.71,0),.18,.205,.42,.19,P); frustum(m,"Thigh.R",(.105,.71,0),.18,.205,.42,.19,P)
    box(m,"Pocket.L",(-.215,.73,.025),(.035,.18,.13),A); box(m,"Pocket.R",(.215,.73,.025),(.035,.18,.13),A)
    # torso has a clear tapered jacket, waist 1.05 and shoulders 1.48
    frustum(m,"Jacket",(0,1.255,0),.38,.55,.43,.26,J)
    box(m,"Hem",(0,1.045,.015),(.39,.045,.28),A)
    # zipper and split collar sit on front (+Z)
    box(m,"Zipper",(0,1.27,.145),(.018,.39,.018),"metal")
    add_poly(m,[(-.02,1.45,.14),(-.20,1.50,.10),(-.08,1.37,.17),(.02,1.45,.14),(.08,1.37,.17),(.20,1.50,.10)],[(0,1,2),(3,4,5)],A,"Collar")
    # arms and distinct exposed hands
    for x,sgn in [(-.34,-1),(.34,1)]:
        frustum(m,"UpperArm."+("L" if x<0 else "R"),(x,1.31,0),.15,.18,.34,.16,J)
        frustum(m,"Forearm."+("L" if x<0 else "R"),(x+sgn*.015,1.08,0),.12,.15,.25,.14,J)
        frustum(m,"Hand."+("L" if x<0 else "R"),(x+sgn*.02,.91,.015),.11,.12,.12,.12,S,6)
    # neck, faceted head, ears, nose make +Z front unmistakable
    frustum(m,"Neck",(0,1.535,0),.15,.16,.13,.15,S,8)
    frustum(m,"Head",(0,1.685,0),.19,.16,.23,.205,S,8)
    add_poly(m,[(-.035,1.69,.105),(.035,1.69,.105),(0,1.64,.145)],[(0,1,2)],S,"Nose")
    for x in (-.052,.052): box(m,"Eye",(x,1.705,.105),(.028,.018,.012),"eye")
    # Short, neutral hair silhouettes; no style represents gameplay information.
    frustum(m,"Hair",(0,1.77,-.002),.17,.12,.06,.205,H,8)
    hair_style=cfg["hair_style"]
    if hair_style in ("left", "right"):
        side=-.092 if hair_style=="left" else .092
        box(m,"HairSide",(side,1.74,-.005),(.022,.08,.14),H)
    elif hair_style=="fringe":
        box(m,"HairFringe",(0,1.765,.099),(.13,.045,.018),H)
    elif hair_style=="crop":
        box(m,"HairCrown",(0,1.795,-.015),(.10,.01,.12),H)
    # recognisable neutral garment detail visible at useful distances
    d=cfg["detail"]
    if d=="shoulder_band":
        box(m,"Band.L",(-.325,1.40,.005),(.18,.045,.17),A); box(m,"Band.R",(.325,1.40,.005),(.18,.045,.17),A)
    elif d=="back_yoke": box(m,"BackYoke",(0,1.40,-.145),(.43,.11,.018),A)
    elif d=="sleeve_cuffs":
        box(m,"Cuff.L",(-.355,1.00,0),(.16,.065,.16),A); box(m,"Cuff.R",(.355,1.00,0),(.16,.065,.16),A)
    elif d=="hem_band": box(m,"BackBand",(0,1.09,-.145),(.38,.07,.018),A)
    elif d=="chest_panel": box(m,"ChestPanel",(0,1.31,.145),(.22,.11,.018),A)
    elif d=="knee_panels":
        box(m,"Knee.L",(-.105,.50,.09),(.14,.10,.018),A); box(m,"Knee.R",(.105,.50,.09),(.14,.10,.018),A)
    elif d=="double_back":
        box(m,"BackBand.Top",(0,1.38,-.145),(.36,.045,.018),A); box(m,"BackBand.Bottom",(0,1.18,-.145),(.32,.045,.018),A)
    elif d=="side_panels":
        box(m,"SidePanel.L",(-.185,1.25,.14),(.055,.27,.018),A); box(m,"SidePanel.R",(.185,1.25,.14),(.055,.27,.018),A)
    return m

def write_glb(name,cfg,m):
    mats=[]; keys=["jacket","pants","skin","hair","accent","shoe","metal","eye"]
    props={"jacket":(.86,0),"pants":(.82,0),"skin":(.68,0),"hair":(.95,0),"accent":(.78,0),"shoe":(.92,0),"metal":(.38,.55),"eye":(.75,0)}
    colors={**cfg,**COMMON}
    for k in keys:
        rough,metal=props[k]; mats.append({"name":k.title(),"pbrMetallicRoughness":{"baseColorFactor":rgb(colors[k]),"metallicFactor":metal,"roughnessFactor":rough}})
    blob=bytearray(); views=[]; acc=[]
    def add_data(data,fmt,typ,target,mins=None,maxs=None):
        while len(blob)%4: blob.append(0)
        off=len(blob); blob.extend(struct.pack('<'+fmt*len(data),*data)); views.append({"buffer":0,"byteOffset":off,"byteLength":len(blob)-off,"target":target})
        a={"bufferView":len(views)-1,"componentType":{"f":5126,"I":5125}[fmt],"count":len(data)//({"VEC3":3,"SCALAR":1}[typ]),"type":typ}
        if mins is not None: a.update(min=mins,max=maxs)
        acc.append(a); return len(acc)-1
    flatv=[q for p in m["v"] for q in p]; flatn=[q for p in m["n"] for q in p]
    pos=add_data(flatv,'f','VEC3',34962,[min(p[j] for p in m['v']) for j in range(3)],[max(p[j] for p in m['v']) for j in range(3)])
    nor=add_data(flatn,'f','VEC3',34962)
    meshes=[]; nodes=[{"name":"CharacterVisual","children":[]}]
    for part,mat,start,count in m["parts"]:
        ind=add_data(m["i"][start:start+count],'I','SCALAR',34963)
        meshes.append({"name":part,"primitives":[{"attributes":{"POSITION":pos,"NORMAL":nor},"indices":ind,"material":keys.index(mat),"mode":4}]})
        nodes.append({"name":part,"mesh":len(meshes)-1}); nodes[0]["children"].append(len(nodes)-1)
    doc={"asset":{"version":"2.0","generator":"Armed Mystery stdlib procedural source"},"scene":0,"scenes":[{"name":"VisualOnly","nodes":[0]}],"nodes":nodes,"meshes":meshes,"materials":mats,"accessors":acc,"bufferViews":views,"buffers":[{"byteLength":len(blob)}],"extras":{"variant":name,"orientation":"Y up; +Z model front; origin at soles","units":"meters"}}
    js=json.dumps(doc,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4); blob+=b'\0'*((4-len(blob)%4)%4)
    data=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(blob))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(blob),b'BIN\0')+blob
    (OUT/f"mystery_character_{name}.glb").write_bytes(data)

def png(path,w,h,pix):
    raw=b''.join(b'\0'+bytes(pix[y*w*3:(y+1)*w*3]) for y in range(h))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def render(path, items, view="perspective", dark=False, size=(720,720)):
    w,h=size; bg=(14,17,23) if dark else (224,225,221); pix=list(bg)*(w*h); zbuf=[1e9]*(w*h)
    light=norm((-1,2,2)); scale=min(w/(len(items)*.85),h/2.05)*.78
    for slot,(m,cfg) in enumerate(items):
        colors={**cfg,**COMMON}; ox=(slot+.5)*w/len(items); oy=h*.94
        for part,mat,start,count in m["parts"]:
            col=[int(x*255) for x in rgb(colors[mat])[:3]]
            for k in range(start,start+count,3):
                pts=[]; depths=[]
                for ii in m["i"][k:k+3]:
                    x,y,z=m["v"][ii]
                    if view=="side": X=z; Z=x
                    elif view=="front": X=x; Z=-z
                    else: X=.82*x+.55*z; Z=.82*z-.55*x
                    pts.append((ox+X*scale,oy-y*scale)); depths.append(-Z)
                no=m["n"][m["i"][k]]; shade=max(.28,min(1,.38+.62*abs(sum(no[j]*light[j] for j in range(3)))))
                cc=tuple(min(255,int(q*shade+(12 if dark else 8))) for q in col)
                x0=max(0,int(min(p[0] for p in pts))); x1=min(w-1,int(max(p[0] for p in pts))+1); y0=max(0,int(min(p[1] for p in pts))); y1=min(h-1,int(max(p[1] for p in pts))+1)
                ax,ay=pts[0]; bx,by=pts[1]; cx,cy=pts[2]; den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
                if abs(den)<1e-6: continue
                for yy in range(y0,y1+1):
                    for xx in range(x0,x1+1):
                        a=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den; b=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den; d=1-a-b
                        if a>=0 and b>=0 and d>=0:
                            zz=a*depths[0]+b*depths[1]+d*depths[2]; q=yy*w+xx
                            if zz<zbuf[q]: zbuf[q]=zz; pix[q*3:q*3+3]=cc
    png(path,w,h,pix)

def main():
    OUT.mkdir(exist_ok=True); PRE.mkdir(exist_ok=True); built=[]
    for old in OUT.glob('mystery_character_*.glb'): old.unlink()
    for name,cfg in VARIANTS.items():
        m=build(cfg); write_glb(name,cfg,m); built.append((m,cfg))
    base=[built[0]]
    render(PRE/'base_front.png',base,'front'); render(PRE/'base_side_plus_z_front.png',base,'side')
    render(PRE/'base_perspective.png',base,'perspective'); render(PRE/'variants_lineup.png',built,'front',size=(1920,640))
    render(PRE/'dark_lighting.png',built,'perspective',dark=True,size=(1920,640))
    print(json.dumps({n:len(build(c)['i'])//3 for n,c in VARIANTS.items()},indent=2))

if __name__=='__main__': main()
