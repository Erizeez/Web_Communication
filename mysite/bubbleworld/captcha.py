# -*- coding: utf-8 -*-
import random
from io import StringIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

lower_cases = 'abcdefghijklmnopqrstuvwxyz'
upper_cases = lower_cases.upper()
numbers = ''.join(map(str, range(10)))
init_chars = ''.join((
        lower_cases,
        upper_cases,
        numbers
        ))

def create_captcha(
        size = (100, 40),
        chars = init_chars,
        img_type = 'GIF',
        mode = 'RGB',
        bg_color = (255, 255, 255),
        fg_color = (0, 0, 0),
        font_size = 20,
        font_type = 'bubbleworld/fonts/Apple.ttf',
        length = 4,
        draw_points = True,
        point_chance = 2
        ):
    width, height = size
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    def get_chars():
        return random.sample(chars, length)
    
    def create_points():
        chance = min(
                100, 
                max(0, int(point_chance))
                )

        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))
    
    def create_strs():
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)

        draw.text(((width - font_width) / 3, 
                   (height - font_height) / 3
                   ),
                  strs,
                  font=font,
                  fill=fg_color)

        return ''.join(c_chars)
    
    if draw_points:
        create_points()
    strs = create_strs()
    
    params = [
        1 - float(random.randint(1, 2)) / 100, 0, 0, 0,
        1 - float(random.randint(1, 10)) / 100,
        float(random.randint(1, 2)) / 500, 0.001,
        float(random.randint(1, 2)) / 500
    ]
    img = img.transform(size, Image.PERSPECTIVE, params)  

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE) 

    return img, strs


if __name__ == "__main__":
    mstream = StringIO.StringIO()
    code_img = create_captcha()[0]
    code_img.save("validate.gif", "GIF")
   
    
    
    
    
    
    
