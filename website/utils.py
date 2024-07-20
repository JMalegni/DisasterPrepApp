import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans, get_language
<<<<<<< HEAD
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor
=======
>>>>>>> e1ab7c2ec00d4997d254b1df89749560e9b12e42

def parse_furigana(text: str) -> tuple[str, list[tuple[str, str]]]:
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    matches = ruby_pattern.findall(text)
    parsed_text = []
    for match in matches:
        base_text, furigana = match
        parsed_text.append((base_text, furigana))
        text = text.replace(f'<ruby>{base_text}<rt>{furigana}</rt></ruby>', base_text)
    return text, parsed_text
<<<<<<< HEAD

def draw_text(draw, text, font, x, y, fill='black'):
    draw.text((x, y), text, font=font, fill=fill)
=======
>>>>>>> e1ab7c2ec00d4997d254b1df89749560e9b12e42

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

def checklist_image(checklist, disaster_type):
    background_path = os.path.join(settings.STATIC_ROOT, 'images', 'template.png')
    background = Image.open(background_path).convert('RGB')

    scale = 4
    new_size = (int(1415 * scale), int(2000 * scale))
    background = background.resize(new_size)

    draw = ImageDraw.Draw(background)
<<<<<<< HEAD
=======
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-VariableFont_wght.ttf')
    font_size = 82
    font = ImageFont.truetype(font_path, font_size)
    furigana_font_size = 25
    furigana_font = ImageFont.truetype(font_path, furigana_font_size)
>>>>>>> e1ab7c2ec00d4997d254b1df89749560e9b12e42

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

<<<<<<< HEAD
    tasks = []
    tasks.append((draw_text, (draw, trans(f"Your checklist for {disaster_type}s"), fonts['title'], 260 * scale, 50 * scale)))
    tasks.append((draw_text, (draw, f"created by S.E.E.L.E on {datetime.now().date()}", fonts['info'], 400 * scale, 140 * scale)))
    tasks.append((draw_text, (draw, "Items to prepare", fonts['header'], 900 * scale, 220 * scale)))
=======
    # Printing out the checklist line by line
    font_size = 37
    font = ImageFont.truetype(font_path, font_size)
    x, y = 100, 160
    draw.text((x, y), trans("Personalized disaster checklist:"), font=font, fill='black')
>>>>>>> e1ab7c2ec00d4997d254b1df89749560e9b12e42

    y = 310 * scale
    for i, item in enumerate(checklist):
        x = 750 * scale
        if get_language().startswith("jp"):
            sentence_furi = parse_furigana(item)
            tasks.append((draw_text, (draw, f"- {sentence_furi[1]}", fonts['items'], x, y)))
            y += 37 * scale
            tasks.append((draw_text, (draw, f"- {sentence_furi[0]}", fonts['items'], x, y)))
        elif get_language().startswith("en"):
            tasks.append((draw_text, (draw, f"- {item}", fonts['items'], x, y)))
        y += 37 * scale

<<<<<<< HEAD
    if disaster_type == "Typhoon":
        typhoon_checklist(draw, fonts, scale)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(func, *args) for func, args in tasks]
        for future in futures:
            future.result()
=======
    for item in checklist:
        if get_language().startswith("jp"):
            sentence_furi = parse_furigana(item)
            draw.text((x, y), f"- {sentence_furi[1]}", font=font, fill='black')
            y += 37
            draw.text((x, y), f"- {sentence_furi[0]}", font=font, fill='black')
            y += 37
        elif get_language().startswith("en"):
            draw.text((x, y), item, font=font, fill='black')
            y += 37

    # REMINDER TO MAKE TEXT DRAW FUNCTION 
    if disaster_type == "Typhoon":
        if get_language().startswith("en"):
            before_typhoon = [
                ("Before a level 1 typhoon:"),
                ("- Check a hazard map"),
                ("- Find nearby evacuation centers"),
                ("- Make sure you have every item on the checklist"),
                ("- Beware of possible dangers in your house"),
                ("Before a level 2 typhoon:"),
                ("- Officially decide on an evacuation center"),
                ("- Recheck emergency bags"),
                ("- Prepare for power outage"),
                ("Before a level 3 typhoon:"),
                ("- Elderly people must evacuate"),
                ("- People with disabilities must evacuate"),
                ("Before a level 4 typhoon:"),
                ("- Go to an evacuation center immediately"),
            ]

            typhoon_evac = [
                ("If evacuating by foot:"),
                ("- Do not walk inside water above knee level"),
                ("or with flooding"),
                ("- Do not step on a manhole cover"),
                ("If evacuating by car:"),
                ("- Avoid roads along rivers, areas with"),
                ("rice fields and underpasses"),
                ("- Do not drive into water higher than"),
                ("half of the car wheels"),
                ("During level 5 typhoon:"),
                ("- Watch out for potential landslide"),
                ("- Move away from cliffs and slopes"),
                ("If you can't evacuate safely:"),
                ("- Go to the highest floor of a building and"),
                ("make sure the building is not near a cliff"),
                ("Signs of a landslide:"),
                ("- Pebbles falling from the slope"),
                ("- Cracks appearing on the slope"),
                ("- Water suddenly gushing out of the slope"),
                ("- Water in the river suddenly decreasing"),
                ("""- Hear "mountain rumbling" or "earth rumbling." """),
            ]
        else:
            before_typhoon = [
                ("レベル１台風が来る前に："),
                ("- ハザードマップを見る"),
                ("- 近い避難所を見つける"),
                ("- 全部チェックリストのアイテムの持ちを確認する"),
                ("- 家の危ないことに注意する"),
                ("レベル２台風が来る前に："),
                ("- 避難所にはっきり決める"),
                ("- 非常持ち出し袋を再確認する"),
                ("- 停電の場合のために準備する"),
                ("レベル３台風が来る前に："),
                ("- 年寄りは避難する必要があります。"),
                ("- 障碍者は避難する必要があります。"),
                ("レベル４台風が来る前に："),
                ("- すぐに避難所に行ってください。"),
            ]

            typhoon_evac = [
                ("徒歩で非難する場合は："),
                ("- 膝の高さより高い水の中で歩かないでください。"),
                ("洪水でも歩かないでください。"),
                ("- マンホールの蓋を踏まないでください。"),
                ("車で非難する場合は："),
                ("- こんな環境を避けてください："),
                ("川沿いの道路、田んぼのある地域、高架下"),
                ("- 車の車輪の半分よりも高い水中に運転しないでください。"),
                ("レベル５台風ながら："),
                ("- 地すべりに注意してください。"),
                ("- 斜面や崖から離れてください。"),
                ("安全に非難することができなければ："),
                ("- 崖に近くない建物で、一番高い階に行ってください。"),
                ("地すべりが始まる合図："),
                ("- 斜面から小石が落ちる"),
                ("- 斜面に亀裂が現れる"),
                ("- 斜面から水が急に湧出する"),
                ("- 川の水が急に減る"),
                ("- 山鳴りが聞こえる"),
            ]
    
        x, y = 790, 150
>>>>>>> e1ab7c2ec00d4997d254b1df89749560e9b12e42

    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
