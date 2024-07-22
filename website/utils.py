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

def bullet_spacing(draw, fonts, list, x, y, scale, bigList=False):
    bullet_font = fonts['bullet']

    if not bigList:
        text_font = fonts['text']

    else:
        text_font = fonts['text2']
    
    for item, bullet_point in list:
        if bullet_point:
            draw_text(draw, "\u2022", bullet_font, x, y)
            draw_text(draw, trans(item), text_font, x + int(40 * scale), y + int(27 * scale))

            if not bigList:
                y += int(46 * scale)

            else:
                y += int(42 * scale)
        else:
            draw_text(draw, trans(item), text_font, x + int(40 * scale), y + int(6 * scale))

            if not bigList:
                y += int(22 * scale)

            else:
                y += int(9 * scale)
    return y

def typhoon_flood_checklist(draw, fonts, scale, user, disaster_type):
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
    
    if user.child_bool:
        level3_typhoon = [
            ("Elderly, people with disabilities, and", True),
            ("families with children must evacuate", False),
        ]
    
    else:
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
    
    if disaster_type == "Typhoon":
        disaster_tips = [
            ("Check your house before leaving (window, breaker,", True),
            ("gas valve)", False),
            ("Check yourself and your belongings", True),
            ("Follow the route avoiding dangerous areas", True),
            ("While evacuating, watch out for flooding", True),
            ("If you cant evacuate safely, stay inside and go to", True),
            ("the highest floor", False),
        ]
        
    else:
        disaster_tips = [
            ("Close all windows in your house and make sure", True),
            ("anything outside is moved indoors", False),
            ("Be aware of strong winds as they will make things fly", True),
            ("Avoid places with high water levels", True),
            ("If you cant evacuate safely, stay inside and go to", True),
            ("the highest floor", False),
        ]

    if user.blind_bool or user.deaf_bool or user.wheelchair_bool:
        disaster_tips.append(("Register people who need evacuation support", True))

    if user.child_bool or user.baby_bool:
        disaster_tips.append(("Don't use a baby stroller", True))
        disaster_tips.append(("Use a backpack and always hold your children's hand", True))

    if user.pet_bool:
        disaster_tips.append(("Use a lead, cage, and carry bag during evacuation", True))
        disaster_tips.append(("Keep pets calm so they don't panic", True))
    
    y = bullet_spacing(draw, fonts, level1_typhoon, 145 * scale, 328 * scale, scale)
    y = bullet_spacing(draw, fonts, level2_typhoon, 145 * scale, y + int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_typhoon, 145 * scale, y + int(40 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_typhoon, 145 * scale, y + int(40 * scale), scale)
    bullet_spacing(draw, fonts, level5_typhoon, 145 * scale, y + int(60 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, "Evacuation Guideline", guideline_font, 850 * scale, 1020 * scale)

    if len(disaster_tips) > 11:
        bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale, True)
    
    else:
        bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale)

def earthquake_checklist(draw, fonts, scale):
    header_font = fonts['header']
    draw_text(draw, "During an earthquake,", header_font, 230 * scale, 220 * scale)
    draw_text(draw, "follow these safety steps:", header_font, 230 * scale, 260 * scale)

#information from https://www.jma.go.jp/jma/en/Activities/inttable.html
    level0_earthquake = [
        ("Imperceptible to people, but recorded", True),
        ("by seismometers", False),
    ]

    level1_earthquake = [
        ("Felt slightly by some people keeping quiet", True),
        ("in buildings", False),
    ]

    level2_earthquake = [
        ("Felt by many people keeping quiet in", True),
        ("buildings", False),
        ("Hanging objects swing slightly", True),
    ]

    level3_earthquake = [
        ("Felt by most people in buildings and some", True),
        ("walking", False),
        ("Dishes rattle and electric wires swing.", True),
    ]

    level4_earthquake = [
        ("Hanging objects swing significantly", True),
        ("Unstable ornaments may fall and electric", True),
        ("wires swing significantly", False),
    ]

    level5_earthquake = [
        ("Unsecured furniture may move and fall", True),
        ("Windows may break and roads may sustain", True),
        ("damage, and some walls may collapsse", False),
    ]

    level6_earthquake = [
        ("Unsecured furniture moves and may topple", True),
        ("Impossible to stand or move without crawling", True),
        ("crawling; walls may collapse", False),
    ]

    level7_earthquake = [
        ("Most furniture topples; reinforced walls may", True),
        ("collapse", False),
    ]

#information from https://www.kcif.or.jp/web/en/livingguide/emergency/
    disaster_tips = [
        ("Ensure Safety: Stay calm and prioritize your", True),
        ("safety", False),
        ("Turn Off Utilities: Alert others and turn off gas", True),
        ("and electricity immediately", False),
        ("Secure an Exit: Open doors and windows if", True),
        ("jammed to create an escape route", False),
        ("Handle Fires: Shout for help and extinguish", True),
        ("small fires immediately", False),
        ("Avoid Rush: Exit carefully, watch for", True),
        ("falling debris", False),
        ("Stay Clear of Hazards: Avoid narrow alleys,", True),
        ("cliffs, and rivers; watch for falling objects", False),
        ("Watch for Aftershocks: Prepare for landslides", True),
        ("or tsunamis if near mountains or the sea", False),
        ("Evacuate on Foot: Go to the nearest shelter with", True),
        ("minimal belongings", False),
        ("Help Others: Assist the elderly, disabled,", True),
        ("and injured", False),
        ("Get Accurate Info: Follow reliable sources for", True),
        ("updates and watch out for aftershocks", False),
    ]

    y = bullet_spacing(draw, fonts, level0_earthquake, 810 * scale, 1050 * scale, scale)
    y = bullet_spacing(draw, fonts, level1_earthquake, 810 * scale, y + int(35 * scale), scale)
    y = bullet_spacing(draw, fonts, level2_earthquake, 810 * scale, y + int(15 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_earthquake, 810 * scale, y - int(2 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_earthquake, 810 * scale, y - int(2 * scale), scale)
    y = bullet_spacing(draw, fonts, level5_earthquake, 810 * scale, y - int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level6_earthquake, 810 * scale, y - int(10 * scale), scale)
    bullet_spacing(draw, fonts, level7_earthquake, 810 * scale, y + int(8 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, "Safety Guidelines", guideline_font, 210 * scale, 328 * scale)
    bullet_spacing(draw, fonts, disaster_tips, 55 * scale, 368 * scale, scale)

def checklist_image(checklist, disaster_type, user):
    if disaster_type == "Typhoon" or disaster_type == "Flood":
        background_path = os.path.join(settings.STATIC_ROOT, 'images', 'typhoon_template.png')
        background = Image.open(background_path).convert('RGB')

    elif disaster_type == "Earthquake":
        background_path = os.path.join(settings.STATIC_ROOT, 'images', 'earthquake_template.png')
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
        'text2': ImageFont.truetype(font_path, int(23 * scale)),
        'guideline': ImageFont.truetype(font_path, int(37 * scale)),
        'title': ImageFont.truetype(font_path, int(65 * scale)),
        'info': ImageFont.truetype(font_path, int(38 * scale)),
        'items': ImageFont.truetype(font_path, int(29 * scale)),
    }

    tasks = []
    if disaster_type == "Earthquake":
        tasks.append((draw_text, (draw, trans(f"Your checklist for {disaster_type}s"), fonts['title'], 190 * scale, 35 * scale)))
    
    else:
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

    if disaster_type == "Typhoon" or disaster_type == "Flood":
        typhoon_flood_checklist(draw, fonts, scale, user, disaster_type)

    elif disaster_type == "Earthquake":
        earthquake_checklist(draw, fonts, scale)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func, *args) for func, args in tasks]
        for future in futures:
            future.result()

    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
