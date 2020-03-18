from PIL import Image
import requests
from io import BytesIO


def averageColor(img_url):
    if not img_url:
        return None
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    size = img.size[0]*img.size[1]
    pixels = img.load()
    r = 0
    g = 0
    b = 0
    total = 0
    step = int(size*0.00005)
    
    for x in range(0,img.size[0],step):
        for y in range(0,img.size[1],step):
            r += pixels[x,y][0]
            g += pixels[x,y][1]
            b += pixels[x,y][2]
            total += 1

    r = round(r/total)
    g = round(g/total)
    b = round(b/total)
    return (r,g,b)