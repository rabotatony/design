import numpy as np
from PIL import Image

def extract_features(image_path):
    img = Image.open(image_path).convert("RGB")
    rgb = np.array(img).astype(float) / 255.0
    gray = rgb.mean(axis=2)
    h, w = gray.shape
    feats = {}
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    cy, cx = h//2, w//2
    r_small = min(h,w)//8
    Y, X = np.ogrid[:h, :w]
    low_mask = (Y-cy)**2 + (X-cx)**2 <= r_small**2
    total = mag.sum() + 1e-10
    low_energy = mag[low_mask].sum()
    feats["high_freq_ratio"] = float(1 - low_energy/total)
    from scipy.ndimage import uniform_filter
    blurred = uniform_filter(gray, size=5)
    noise = gray - blurred
    feats["noise_std"] = float(noise.std())
    b = blurred.ravel(); n = noise.ravel()
    lo, hi = b.min(), b.max()
    if hi - lo > 1e-6:
        bins = np.linspace(lo, hi, 11)
        idx = np.clip(np.digitize(b, bins)-1, 0, 9)
        means = np.zeros(10); vsum = np.zeros(10); cnt = np.zeros(10)
        np.add.at(means, idx, b); np.add.at(vsum, idx, n*n); np.add.at(cnt, idx, 1)
        means = means/np.maximum(cnt,1); vars_ = vsum/np.maximum(cnt,1)
        valid = cnt > 20
        if valid.sum() >= 3:
            corr = np.corrcoef(means[valid], vars_[valid])[0,1]
            feats["noise_corr"] = float(corr) if not np.isnan(corr) else 0.0
        else:
            feats["noise_corr"] = 0.0
    else:
        feats["noise_corr"] = 0.0
    hsv_max = rgb.max(axis=2); hsv_min = rgb.min(axis=2)
    sat = np.where(hsv_max>0, (hsv_max-hsv_min)/hsv_max, 0)
    feats["saturation_mean"] = float(sat.mean())
    feats["saturation_std"] = float(sat.std())
    return feats
