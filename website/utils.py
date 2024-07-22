import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans, get_language
from datetime import datetime
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
            draw_text(draw, trans(item), text_font, x + int(40 * scale), y + int(27 * scale))
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
    draw_text(draw, "Evacuation Guideline", guideline_font, 850 * scale, 1020 * scale)
    bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale)

def earthquake_actions(draw, fonts, scale):
    header_font = fonts['header']
    draw_text(draw, "During an earthquake,", header_font, 230 * scale, 220 * scale)
    draw_text(draw, "follow these safety steps:", header_font, 230 * scale, 260 * scale)

#information from https://www.jma.go.jp/jma/en/Activities/inttable.html
    level0_earthquake = [
        ("Imperceptible to people, but recorded by seismometers.", False),
    ]

    level1_earthquake = [
        ("Felt slightly by some people keeping quiet in buildings.", False),
    ]

    level2_earthquake = [
        ("Felt by many people keeping quiet in buildings.", True),
        ("Hanging objects swing slightly.", True),
    ]

    level3_earthquake = [
        ("Felt by most people in buildings and some walking.", True),
        ("Dishes rattle and electric wires swing.", True),
    ]

    level4_earthquake = [
        ("Most people startled; hanging objects swing significantly.", True),
        ("Unstable ornaments may fall and electric wires swing significantly.", True),
    ]

    level5_lower_earthquake = [
        ("Many frightened; unsecured furniture may move.", True),
        ("Windows may break and roads may sustain damage.", True),
    ]

    level5_upper_earthquake = [
        ("Walking difficult; TVs and unsecured furniture may fall.", True),
        ("Windows may break and some walls may collapse.", True),
    ]

    level6_lower_earthquake = [
        ("Difficult to stand; unsecured furniture moves and may topple.", True),
    ]

    level6_upper_earthquake = [
        ("Impossible to stand or move without crawling; walls may collapse.", True),
    ]

    level7_earthquake = [
        ("Most furniture topples; reinforced walls may collapse.", True),
    ]

#information from https://www.kcif.or.jp/web/en/livingguide/emergency/
    disaster_tips = [
        ("1. Ensure Safety: Stay calm and prioritize your safety.", True),
        ("2. Turn Off Utilities: Alert others and turn off gas and electricity immediately.", True),
        ("3. Secure an Exit: Open doors and windows if jammed to create an escape route.", True),
        ("4. Handle Fires: Shout for help and extinguish small fires immediately.", True),
        ("5. Avoid Rush: Exit carefully, watch for falling debris.", True),
        ("6. Stay Clear of Hazards: Avoid narrow alleys, cliffs, and rivers; watch for falling objects.", True),
        ("7. Watch for Aftershocks: Prepare for landslides or tsunamis if near mountains or the sea.", True),
        ("8. Evacuate on Foot: Go to the nearest shelter with minimal belongings.", True),
        ("9. Help Others: Assist the elderly, disabled, and injured.", True),
        ("10. Get Accurate Info: Follow reliable sources for updates and watch out for aftershocks.", True),
    ]

    y = bullet_spacing(draw, fonts, level0_earthquake, 145 * scale, 328 * scale, scale)
    y = bullet_spacing(draw, fonts, level1_earthquake, 145 * scale, y + int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level2_earthquake, 145 * scale, y + int(40 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_earthquake, 145 * scale, y + int(40 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_earthquake, 145 * scale, y + int(60 * scale), scale)
    y = bullet_spacing(draw, fonts, level5_lower_earthquake, 145 * scale, y + int(60 * scale), scale)
    y = bullet_spacing(draw, fonts, level5_upper_earthquake, 145 * scale, y + int(60 * scale), scale)
    y = bullet_spacing(draw, fonts, level6_lower_earthquake, 145 * scale, y + int(60 * scale), scale)
    y = bullet_spacing(draw, fonts, level6_upper_earthquake, 145 * scale, y + int(60 * scale), scale)
    bullet_spacing(draw, fonts, level7_earthquake, 145 * scale, y + int(60 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, "Safety Guidelines", guideline_font, 850 * scale, 1020 * scale)
    bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale)


def checklist_image(checklist, disaster_type):
    background_path = os.path.join(settings.STATIC_ROOT, 'images', 'template.png')
    background = Image.open(background_path).convert('RGB')


    scale = 1
    new_size = (int(1415 * scale), int(2000 * scale))
    background = background.resize(new_size)

    draw = ImageDraw.Draw(background)

    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-Regular.ttf')
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
    tasks.append((draw_text, (draw, f"created by S.E.E.L.E on {datetime.now().date()}", fonts['info'], 400 * scale, 140 * scale)))
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
    elif disaster_type == "Earthquake":
        earthquake_actions(draw, fonts, scale)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func, *args) for func, args in tasks]
        for future in futures:
            future.result()

    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
