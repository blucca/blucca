#!/usr/bin/env python3
"""Regenerate Blucca's original banner. Requires Pillow and fonttools.

Run from any directory: python3 assets/generate-banner.py
Optional: --social /path/to/blucca-site/assets/studio/social.png
All fonts are bundled under their original SIL OFL licenses.
"""
from io import BytesIO
from pathlib import Path
import argparse, math
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
W, H = 1200, 380
INK, COBALT, ICE, CYAN, PEACH = '#172a4b', '#254bdd', '#eaf3ff', '#42d4d8', '#fead82'
MUTED, FIELD, WHITE = '#5b6c83', '#dceaff', '#ffffff'

def font(filename, size, weight):
    f = TTFont(HERE / 'fonts' / filename)
    axes = f['fvar'].axes
    values = [min(max(weight if a.axisTag == 'wght' else 60 if a.axisTag == 'opsz' else a.defaultValue, a.minValue), a.maxValue) for a in axes]
    f.flavor = None
    data = BytesIO()
    f.save(data)
    data.seek(0)
    face = ImageFont.truetype(data, size)
    face.set_variation_by_axes(values)
    return face

TITLE = font('bricolage-grotesque-latin.woff', 79, 700)
WORDMARK = font('bricolage-grotesque-latin.woff', 27, 800)
BODY = font('instrument-sans-latin.woff', 17, 400)
SMALL = font('instrument-sans-latin.woff', 13, 400)
LETTER = font('bricolage-grotesque-latin.woff', 23, 650)

def path(segments):
    points = []
    previous = None
    for s in segments:
        if s[0] == 'M':
            previous = s[1:]
            points.append(previous)
        elif s[0] == 'L':
            points.append(s[1:])
            previous = s[1:]
        elif s[0] == 'Q':
            x0, y0 = previous
            x1, y1, x2, y2 = s[1:]
            for k in range(1, 13):
                t = k / 12
                points.append(((1-t)**2*x0+2*(1-t)*t*x1+t*t*x2, (1-t)**2*y0+2*(1-t)*t*y1+t*t*y2))
            previous = (x2, y2)
    return points

D = path([('M',72,208),('L',150,208),('Q',178,208,178,180),('L',178,140),('Q',178,122,196,122),('L',292,122),('Q',312,122,312,142),('L',312,190),('Q',312,208,332,208),('L',464,208)])
C = path([('M',72,270),('L',122,270),('Q',144,270,144,248),('L',144,184),('Q',144,166,162,166),('L',246,166),('Q',268,166,268,144),('L',268,98),('Q',268,78,288,78),('L',464,78)])

def point_at(points, fraction):
    lengths = [math.dist(a,b) for a,b in zip(points,points[1:])]
    distance = sum(lengths) * fraction
    for index, length in enumerate(lengths):
        if distance <= length:
            a,b = points[index:index+2]
            ratio = distance/length if length else 0
            return (a[0]+(b[0]-a[0])*ratio, a[1]+(b[1]-a[1])*ratio)
        distance -= length
    return points[-1]

OX, OY = 642, 17

def translated(points):
    return [(x+OX,y+OY) for x,y in points]

def circle(draw, xy, radius, fill, outline=None, width=1):
    x,y = xy
    draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=fill,outline=outline,width=width)

def base():
    im = Image.new('RGB',(W,H),ICE)
    d = ImageDraw.Draw(im)
    d.text((50,26),'blucca',font=WORDMARK,fill=INK)
    for angle in (0,60,120):
        a=math.radians(angle)
        x,y=151,45
        dx,dy=9*math.cos(a),9*math.sin(a)
        d.line((x-dx,y-dy,x+dx,y+dy),fill=COBALT,width=3)
    d.text((47,102),'Follow the',font=TITLE,fill=INK)
    d.text((47,180),'right thread.',font=TITLE,fill=INK)
    d.text((52,309),'n8n tools & open research',font=BODY,fill=MUTED)
    # This is a route illustration, not a measured execution screenshot.
    d.rounded_rectangle((OX+115,OY+23,OX+416,OY+318),radius=79,fill=FIELD)
    d.line(translated(D),fill=COBALT,width=5,joint='curve')
    d.line(translated(C),fill=CYAN,width=5,joint='curve')
    d.text((OX+18,OY+150),'Source item',font=SMALL,fill=MUTED)
    d.text((OX+405,OY+24),'HTTP recipient',font=SMALL,fill=MUTED)
    for x,y,char in ((46,208,'D'),(46,270,'C'),(490,208,'D'),(490,78,'C')):
        circle(d,(OX+x,OY+y),27,WHITE,INK,2)
        d.text((OX+x,OY+y-1),char,font=LETTER,fill=INK,anchor='mm')
    d.line([(OX+206,OY+98),(OX+242,OY+98)],fill='#a6bfdb',width=2)
    d.line([(OX+224,OY+98),(OX+224,OY+196)],fill='#a6bfdb',width=2)
    d.line([(OX+206,OY+196),(OX+242,OY+196)],fill='#a6bfdb',width=2)
    d.text((OX+224,OY+240),'Child workflow',font=SMALL,fill=MUTED,anchor='mm')
    return im


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--social',type=Path)
    args=parser.parse_args()
    still=base()
    still.save(HERE/'banner-still.png',optimize=True)
    # A fixed palette keeps the stable lettering identical through all frames.
    palette=still.quantize(colors=128,method=Image.Quantize.MEDIANCUT)
    frames=[]
    for k in range(56):
        im=still.copy()
        draw=ImageDraw.Draw(im)
        for route, fraction in ((D,k/56),(C,((k/56)+.2857)%1)):
            x,y=point_at(route,fraction)
            circle(draw,(x+OX,y+OY),8,WHITE)
            circle(draw,(x+OX,y+OY),5,INK)
        frames.append(im.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(HERE/'banner.gif',save_all=True,append_images=frames[1:],duration=[120 if k%2==0 else 130 for k in range(56)],loop=0,optimize=True,disposal=1)
    if args.social:
        social=Image.new('RGB',(1200,630),ICE)
        social.paste(still,(0,125))
        social.save(args.social,optimize=True)
    print(f'GIF: {(HERE/"banner.gif").stat().st_size:,} bytes, {len(frames)} frames, 7 seconds')

if __name__=='__main__':
    main()
