def bilerp(TL, TR, BL, BR, u, v):
    x = (1-v)*((1-u)*TL[0] + u*TR[0]) + v*((1-u)*BL[0] + u*BR[0])
    y = (1-v)*((1-u)*TL[1] + u*TR[1]) + v*((1-u)*BL[1] + u*BR[1])
    return (round(x, 1), round(y, 1))

# ── Your 8 cube corners ──────────────────────────────────────────
# Label:  A=top-back-left   B=top-back-right
#         C=top-front-left  D=top-front-right
#         E=bot-front-left  G=bot-front-right  H=bot-back-right
A=(246,41);  B=(499,73)
C=(96,109);  D=(384,154)
E=(109,397); F=(247,328); G=(379,458);  H=(493,342)

# ── Face functions (TL, TR, BL, BR per face) ────────────────────
def front(u,v): return bilerp(C, D, E, G, u, v)
def top(u,v):   return bilerp(A, B, C, D, u, v)
def right(u,v): return bilerp(D, B, G, H, u, v)
def back(u,v):  return bilerp(A, B, F, H, u, v)   # ✅ fixed
def left(u,v):  return bilerp(A, C, F, E, u, v)   # ✅ fixed
def bot(u,v):   return bilerp(E, G, F, H, u, v)

# ── Grid size: change this one number ───────────────────────────
N = 5   # 2=2x2  3=3x3  4=4x4  5=5x5  etc.

# ── Generate SVG polygons ────────────────────────────────────────
def pt(p):        return f"{p[0]},{p[1]}"
def poly(a,b,c,d): return f"{pt(a)} {pt(b)} {pt(c)} {pt(d)}"

for face_name, face_fn in [("FRONT", front), ("TOP", top), ("RIGHT", right), ("BACK", back), ("LEFT", left), ("BOT", bot)]:
    print(f"<!-- {face_name} -->")
    for row in range(N):
        for col in range(N):
            tl = face_fn( col/N,     row/N    )
            tr = face_fn((col+1)/N,  row/N    )
            br = face_fn((col+1)/N, (row+1)/N )
            bl = face_fn( col/N,    (row+1)/N )
            print(f'<polygon points="{poly(tl,tr,br,bl)}"/>')
    print()