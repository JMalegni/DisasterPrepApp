import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans, get_language

def parse_furigana(text: str) -> tuple[str, list[tuple[str, str]]]:
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    matches = ruby_pattern.findall(text)
    parsed_text = []
    for match in matches:
        base_text, furigana = match
        parsed_text.append((base_text, furigana))
        text = text.replace(f'<ruby>{base_text}<rt>{furigana}</rt></ruby>', base_text)
    return text, parsed_text

def checklist_image(checklist, disaster_type, facts):
    # Loading the image template from static folder
    background_path = os.path.join(settings.STATIC_ROOT, 'images', 'template_test.png')
    background = Image.open(background_path).convert('RGB')

    # Ensure the background image has the Japanese A4 paper size (1414 x 2000).
    background = background.resize((1414, 2000))

    draw = ImageDraw.Draw(background)
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-VariableFont_wght.ttf')
    font_size = 82
    font = ImageFont.truetype(font_path, font_size)
    furigana_font_size = 25
    furigana_font = ImageFont.truetype(font_path, furigana_font_size)

    # Position and creation of disaster name
    x, y = 550, 0
    draw.text((x, y), trans(disaster_type), font=font, fill='black')

    # Printing out the checklist line by line
    font_size = 37
    font = ImageFont.truetype(font_path, font_size)
    x, y = 100, 160
    draw.text((x, y), trans("Personalized disaster checklist:"), font=font, fill='black')

    font_size = 25
    font = ImageFont.truetype(font_path, font_size)
    x, y = 115, 210

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

        for item in before_typhoon:
            if ':' in item:
                y += 10
                font_size = 37
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), f"{trans(item)}", font=font, fill='black')
                y += 45

            else:
                x += 15
                font_size = 25
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), f"{trans(item)}", font=font, fill='black')
                x -= 15
                y += 37
        
        x, y = 790, 1080

        for item in typhoon_evac:
            if ':' in item:
                y += 10
                font_size = 37
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), f"{trans(item)}", font=font, fill='black')
                y += 45

            elif '-' in item:
                x += 15
                font_size = 25
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), f"{trans(item)}", font=font, fill='black')
                x -= 15
                y += 37

            else:
                x += 30
                y -= 10
                font_size = 25
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), f"{trans(item)}", font=font, fill='black')
                x -= 30
                y += 37

    # Naming and saving file to static folder
    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
