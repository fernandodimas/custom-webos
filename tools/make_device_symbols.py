"""Creates device brand symbol PNGs for use as CSS masks in the TV home app."""
import math, os, sys
from PIL import Image, ImageDraw
SZ, PAD = 200, 16
def new_canvas():
    return Image.new("RGBA", (SZ + 2 * PAD, SZ + 2 * PAD), (0, 0, 0, 0))
def save(img, path, name):
    os.makedirs(path, exist_ok=True)
    img.save(os.path.join(path, name), optimize=True)
    print("  ->", name)
def make_xbox(out):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    cx = cy = (SZ + 2 * PAD) // 2
    r = SZ // 2
    ring = 14
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,255,255,255))
    draw.ellipse([cx-r+ring, cy-r+ring, cx+r-ring, cy+r-ring], fill=(0,0,0,0))
    arm_w = 34
    reach = int(r * 0.60)
    def arm(angle_deg, length, width_px):
        angle = math.radians(angle_deg)
        perp = math.radians(angle_deg + 90)
        tip_x = cx + math.cos(angle) * length
        tip_y = cy + math.sin(angle) * length
        dx = math.cos(perp) * width_px / 2
        dy = math.sin(perp) * width_px / 2
        draw.polygon([(cx+dx,cy+dy),(tip_x+dx,tip_y+dy),(tip_x-dx,tip_y-dy),(cx-dx,cy-dy)], fill=(255,255,255,255))
    for a in [45, 135, 225, 315]:
        arm(a, reach, arm_w)
    cr = 14
    draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(255,255,255,255))
    save(img, out, "xbox.png")
def make_playstation(out):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    total = SZ + 2 * PAD
    cx = cy = total // 2
    cell = SZ // 4
    def ring(x, y, r):
        rng = max(3, r//5)
        draw.ellipse([x-r,y-r,x+r,y+r], fill=(255,255,255,255))
        draw.ellipse([x-r+rng,y-r+rng,x+r-rng,y+r-rng], fill=(0,0,0,0))
    xl, yl, bar_w = cx-cell, cy+cell//2, 8
    for ang in [45, 135]:
        a, p = math.radians(ang), math.radians(ang+90)
        ln = cell * 0.7
        draw.polygon([(xl+math.cos(p)*bar_w, yl+math.sin(p)*bar_w),(xl-math.cos(p)*bar_w, yl-math.sin(p)*bar_w),(xl+math.cos(a)*ln-math.cos(p)*bar_w, yl+math.sin(a)*ln-math.sin(p)*bar_w),(xl+math.cos(a)*ln+math.cos(p)*bar_w, yl+math.sin(a)*ln+math.sin(p)*bar_w)], fill=(255,255,255,255))
        draw.polygon([(xl+math.cos(p)*bar_w, yl+math.sin(p)*bar_w),(xl-math.cos(p)*bar_w, yl-math.sin(p)*bar_w),(xl-math.cos(a)*ln-math.cos(p)*bar_w, yl-math.sin(a)*ln-math.sin(p)*bar_w),(xl-math.cos(a)*ln+math.cos(p)*bar_w, yl-math.sin(a)*ln+math.sin(p)*bar_w)], fill=(255,255,255,255))
    ring(cx+cell, cy+cell//2, int(cell*0.65))
    xt, yt = cx+cell, cy-cell//2
    tri_r = int(cell*0.7)
    pts = [(xt+math.cos(math.radians(-90+i*120))*tri_r, yt+math.sin(math.radians(-90+i*120))*tri_r) for i in range(3)]
    draw.polygon(pts, fill=(255,255,255,255))
    inner_r = int(tri_r*0.55)
    inner_pts = [(xt+math.cos(math.radians(-90+i*120))*inner_r, yt+math.sin(math.radians(-90+i*120))*inner_r) for i in range(3)]
    draw.polygon(inner_pts, fill=(0,0,0,0))
    xs, ys = cx-cell, cy-cell//2
    sq_r = int(cell*0.60)
    sq_w = max(5, sq_r//5)
    draw.rectangle([xs-sq_r,ys-sq_r,xs+sq_r,ys+sq_r], fill=(255,255,255,255))
    draw.rectangle([xs-sq_r+sq_w,ys-sq_r+sq_w,xs+sq_r-sq_w,ys+sq_r-sq_w], fill=(0,0,0,0))
    save(img, out, "playstation.png")
def make_nintendo(out):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    total = SZ + 2 * PAD
    cx = cy = total // 2
    jw = SZ // 5
    jh = SZ // 2 + 10
    cr = jw // 2
    gap = SZ // 12
    lx = cx - gap - jw - jw//2
    draw.rounded_rectangle([lx, cy-jh//2, lx+jw, cy+jh//2], radius=cr, fill=(255,255,255,255))
    rx = cx + gap + jw//2
    draw.rounded_rectangle([rx, cy-jh//2, rx+jw, cy+jh//2], radius=cr, fill=(255,255,255,255))
    sw = SZ//2 - gap*2
    sh = int(jh*0.75)
    draw.rounded_rectangle([cx-sw//2, cy-sh//2, cx+sw//2, cy+sh//2], radius=8, fill=(255,255,255,255))
    si = 8
    draw.rounded_rectangle([cx-sw//2+si, cy-sh//2+si, cx+sw//2-si, cy+sh//2-si], radius=4, fill=(0,0,0,0))
    save(img, out, "nintendo.png")
def make_appletv(out):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    total = SZ + 2 * PAD
    cx = total // 2
    cy = total // 2 + SZ // 16
    ew = int(SZ * 0.42)
    eh = int(SZ * 0.48)
    draw.ellipse([cx-ew, cy-eh//2, cx, cy+eh//2], fill=(255,255,255,255))
    draw.ellipse([cx, cy-eh//2, cx+ew, cy+eh//2], fill=(255,255,255,255))
    draw.ellipse([cx-ew//3, cy-eh//2, cx+ew//3, cy+eh//2], fill=(255,255,255,255))
    bite_r = int(ew * 0.55)
    draw.ellipse([cx+ew-bite_r, cy-eh//2-bite_r//2, cx+ew+bite_r//2, cy-eh//2+bite_r], fill=(0,0,0,0))
    stem_w = max(6, SZ//25)
    stem_h = SZ // 8
    draw.rounded_rectangle([cx-stem_w//2, cy-eh//2-stem_h, cx+stem_w//2, cy-eh//2+4], radius=stem_w//2, fill=(255,255,255,255))
    lw, lh = SZ//6, SZ//14
    leaf_cx = cx + lw//2
    leaf_cy = cy - eh//2 - stem_h//2
    draw.ellipse([leaf_cx-lw//2, leaf_cy-lh, leaf_cx+lw//2, leaf_cy+lh], fill=(255,255,255,255))
    save(img, out, "appletv_device.png")
def make_firetv(out):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    total = SZ + 2 * PAD
    cx = total // 2
    cy = total // 2 + SZ // 10
    r = SZ // 2
    pts = [(cx,cy-r),(cx+r*0.45,cy-r*0.5),(cx+r*0.5,cy),(cx+r*0.35,cy+r*0.5),(cx,cy+r*0.55),(cx-r*0.35,cy+r*0.5),(cx-r*0.5,cy),(cx-r*0.45,cy-r*0.5)]
    draw.polygon(pts, fill=(255,255,255,255))
    ri = int(r * 0.5)
    pts2 = [(cx,cy-ri*0.8),(cx+ri*0.3,cy-ri*0.2),(cx+ri*0.35,cy+ri*0.3),(cx,cy+ri*0.45),(cx-ri*0.35,cy+ri*0.3),(cx-ri*0.3,cy-ri*0.2)]
    draw.polygon(pts2, fill=(0,0,0,0))
    save(img, out, "firetv.png")
if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "out/symbols_test"
    print("Generating device symbols ->", out_dir)
    make_xbox(out_dir)
    make_playstation(out_dir)
    make_nintendo(out_dir)
    make_appletv(out_dir)
    make_firetv(out_dir)
    print("Done.")
