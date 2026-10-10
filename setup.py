import os, shutil
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
L = os.path.join(D, "lib")

# 1) ตั้งชื่อไฟล์เอนจินให้ตรงกับที่ loader คาดไว้
for a, b in (("sf19.js", "stockfish.js"), ("sf19.wasm", "stockfish.wasm")):
    p, q = os.path.join(L, a), os.path.join(L, b)
    if os.path.exists(p):
        shutil.move(p, q)
print("lib:", sorted(os.listdir(L)))
for f in sorted(os.listdir(L)):
    print(f"   {f}  {os.path.getsize(os.path.join(L,f)):,} B")

# 2) ไอคอน
def make_icon(size, path):
    try:
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (size, size), "#15181c")
        d = ImageDraw.Draw(im)
        m = size // 8
        d.rounded_rectangle([m, m, size - m, size - m], radius=size // 10, fill="#1e2228", outline="#f0a04b", width=max(2, size // 90))
        # ตัวหมาก (วาดคร่าว ๆ จากวงกลม/สี่เหลี่ยม)
        cx = size // 2
        d.ellipse([cx - size*0.16, size*0.16, cx + size*0.16, size*0.48], fill="#e9edf2")          # หัว
        d.rectangle([cx - size*0.10, size*0.44, cx + size*0.10, size*0.62], fill="#e9edf2")        # คอ
        d.polygon([(cx - size*0.26, size*0.62), (cx + size*0.26, size*0.62), (cx + size*0.34, size*0.78), (cx - size*0.34, size*0.78)], fill="#e9edf2")
        d.rectangle([cx - size*0.36, size*0.78, cx + size*0.36, size*0.86], fill="#f0a04b")
        im.save(path, "PNG")
        return True
    except Exception as e:
        print("   (PIL ไม่มี → ข้ามไอคอน:", e, ")")
        return False

for s in (180, 512):
    print("icon", s, make_icon(s, os.path.join(D, f"icon-{s}.png")))

print("\nไฟล์ในโฟลเดอร์แอพ:")
for f in sorted(os.listdir(D)):
    p = os.path.join(D, f)
    print(f"   {'DIR ' if os.path.isdir(p) else f'{os.path.getsize(p):>9,} B'}  {f}")
