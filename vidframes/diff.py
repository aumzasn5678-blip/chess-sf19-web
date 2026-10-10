import numpy as np, glob, os
from PIL import Image
files = sorted(glob.glob('vidframes/f_*.png'))
imgs = [np.asarray(Image.open(f).convert('RGB'), dtype=np.int16) for f in files]
n = len(imgs)
print('frames', n, 'shape', imgs[0].shape)
# global frame-to-frame mean abs diff
for i in range(1, n):
    d = np.abs(imgs[i]-imgs[i-1]).mean()
    if d > 0.5:
        print(f'{files[i-1]} -> {files[i]}: meandiff={d:.2f}')
# also cumulative vs frame1
print('--- vs frame1 ---')
for i in range(0, n, 5):
    d = np.abs(imgs[i]-imgs[0]).mean()
    print(f'{files[i]}: {d:.2f}')
