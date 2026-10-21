"""Crops the application screenshots (app_*.png) to their content so they are readable in the report.
Idempotent: running it again changes nothing."""
import glob
import os

from PIL import Image, ImageChops

SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
MARGIN = 14

for f in sorted(glob.glob(os.path.join(SHOTS, "app_*.png"))):
    im = Image.open(f).convert("RGB")
    name = os.path.basename(f)
    if "health" in name:
        # JSON viewer page: keep only the top strip
        im = im.crop((0, 0, min(im.width, 700), min(im.height, 90)))
        im.save(f)
        print("trimmed", name, im.size)
        continue
    bg_colour = im.getpixel((im.width - 1, im.height - 1))
    bg = Image.new("RGB", im.size, bg_colour)
    bbox = ImageChops.difference(im, bg).getbbox()
    if not bbox:
        continue
    l, t, r, b = bbox
    box = (max(l - MARGIN, 0), max(t - MARGIN, 0), min(r + MARGIN, im.width), min(b + MARGIN, im.height))
    # keep a sensible minimum width so tiny pages are not blown up
    if box[2] - box[0] < 520:
        box = (box[0], box[1], min(box[0] + 520, im.width), box[3])
    im.crop(box).save(f)
    print("cropped", name, im.crop(box).size)
