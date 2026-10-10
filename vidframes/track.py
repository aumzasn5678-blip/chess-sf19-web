import numpy as np, glob
from PIL import Image
files = sorted(glob.glob('vidframes/f_*.png'))
# board crop region
X0,Y0,W,H = 70,270,372,412
prev=None
print("frame  npx   cx    cy    bb(x0,y0,x1,y1)")
for i,f in enumerate(files):
    im = np.asarray(Image.open(f).convert('RGB'), dtype=np.int16)[Y0:Y0+H, X0:X0+W]
    R,G,B = im[:,:,0],im[:,:,1],im[:,:,2]
    # bright saturated green (highlight outline / arrow), NOT the dark pieces
    mask = (G>120)&(G-R>50)&(G-B>40)
    n = int(mask.sum())
    if n>30:
        ys,xs = np.where(mask)
        cx,cy = xs.mean(), ys.mean()
        bb=(xs.min(),ys.min(),xs.max(),ys.max())
        print(f"{f[-7:-4]}  {n:5d} {cx:6.1f} {cy:6.1f}  {bb}")
