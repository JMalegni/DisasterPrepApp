import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans, get_language
import re
from concurrent.futures import ThreadPoolExecutor

def parse_furigana(text: str) -> tuple[str, list[tuple[str, str]]]:
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    matches = ruby_pattern.findall(text)
    parsed_text = []
    for match in matches:
        base_text, furigana = match
        parsed_text.append((base_text, furigana))
        text = text.replace(f'<ruby>{base_text}<rt>{furigana}</rt></ruby>', base_text)
    return text, parsed_text

def draw_text(draw, text, font, x, y, fill='black'):
    draw.text((x, y), text, font=font, fill=fill)

def bullet_spacing(draw, fonts, list, x, y, scale):
    bullet_font = fonts['bullet']
    text_font = fonts['text']
    
    for item, bullet_point in list:
        if bullet_point:
            draw_text(draw, "\u2022", bullet_font, x, y)
            draw_text(draw, trans(item), text_font, x + int(40 * scale), y + int(20 * scale))
            y += int(46 * scale)
        else:
            draw_text(draw, trans(item), text_font, x + int(40 * scale), y + int(6 * scale))
            y += int(22 * scale)
    return y

def typhoon_checklist(draw, fonts, scale):
    header_font = fonts['header']
    draw_text(draw, "Typhoons come with", header_font, 230 * scale, 220 * scale)
    draw_text(draw, "rains, floods, landslides", header_font, 230 * scale, 260 * scale)

    level1_typhoon = [
        ("Check a hazard map", True),
        ("Find evacuation centers", True),
        ("Check items on checklist", True),
        ("Beware of falling things in your", True),
        ("house", False),
    ]
    
    level2_typhoon = [
        ("Decide on evacuation center", True),
        ("Recheck emergency bags", True),
        ("Prepare for power outage", True),
    ]
    
    level3_typhoon = [
        ("Elderly & people with disabilities", True),
        ("must evacuate", False),
    ]
    
    level4_typhoon = [
        ("Go to an evacuation center", True),
        ("immediately", False),
    ]
    
    level5_typhoon = [
        ("Save your life!", True),
    ]
    
    disaster_tips = [
        ("Check your house before leaving (window, breaker,", True),
        ("gas valve)", False),
        ("Check yourself and your belongings", True),
        ("Follow the route avoiding dangerous areas", True),
        ("While evacuating, watch out for flooding", True),
        ("If you cant evacuate safely, stay inside and go to", True),
        ("the highest floor", False),
    ]
    
    y = bullet_spacing(draw, fonts, level1_typhoon, 145 * scale, 328 * scale, scale)
    y = bullet_spacing(draw, fonts, level2_typhoon, 145 * scale, y + int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_typhoon, 145 * scale, y + int(40 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_typhoon, 145 * scale, y + int(40 * scale), scale)
    bullet_spacing(draw, fonts, level5_typhoon, 145 * scale, y + int(60 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, "Evacuation Guideline", guideline_font, 880 * scale, 1025 * scale)
    bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale)

def checklist_image(checklist, disaster_type, facts):
    background_path = os.path.join(settings.STATIC_ROOT, 'images', 'template.png')
    background = Image.open(background_path).convert('RGB')

    scale = 1
    new_size = (int(1415 * scale), int(2000 * scale))
    background = background.resize(new_size)

    draw = ImageDraw.Draw(background)

    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-VariableFont_wght.ttf')
    fonts = {
        'header': ImageFont.truetype(font_path, int(33 * scale)),
        'bullet': ImageFont.truetype(font_path, int(55 * scale)),
        'text': ImageFont.truetype(font_path, int(25 * scale)),
        'guideline': ImageFont.truetype(font_path, int(37 * scale)),
        'title': ImageFont.truetype(font_path, int(65 * scale)),
        'info': ImageFont.truetype(font_path, int(38 * scale)),
        'items': ImageFont.truetype(font_path, int(29 * scale)),
    }

    tasks = []
    tasks.append((draw_text, (draw, trans(f"Your checklist for {disaster_type}s"), fonts['title'], 260 * scale, 50 * scale)))
    tasks.append((draw_text, (draw, "created by S.E.E.L.E date/time/username", fonts['info'], 400 * scale, 140 * scale)))
    tasks.append((draw_text, (draw, "Items to prepare", fonts['header'], 900 * scale, 220 * scale)))

    y = 310 * scale
    for i, item in enumerate(checklist["Go Bag"]):
        x = 750 * scale
        if get_language().startswith("jp"):
            sentence_furi = parse_furigana(item)
            tasks.append((draw_text, (draw, f"- {sentence_furi[1]}", fonts['items'], x, y)))
            y += 37 * scale
            tasks.append((draw_text, (draw, f"- {sentence_furi[0]}", fonts['items'], x, y)))
        elif get_language().startswith("en"):
            tasks.append((draw_text, (draw, f"- {item}", fonts['items'], x, y)))
        y += 37 * scale

    if disaster_type == "Typhoon":
        typhoon_checklist(draw, fonts, scale)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func, *args) for func, args in tasks]
        for future in futures:
            future.result()

    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
