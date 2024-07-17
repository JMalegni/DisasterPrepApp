import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans
import re

def remove_furigana(text):
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    return ruby_pattern.sub(r'\1', text)


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

    # Position and creation of disaster name
    x, y = 550, 0
    draw.text((x, y), trans(disaster_type), font=font, fill='black')

    # Printing out the checklist line by line
    font_size = 37
    font = ImageFont.truetype(font_path, font_size)
    x, y = 100, 160
    draw.text((x, y), "Personalized disaster checklist:", font=font, fill='black')

    font_size = 25
    font = ImageFont.truetype(font_path, font_size)
    x, y = 115, 210

    for item in checklist:
        draw.text((x, y), f"- {remove_furigana(trans(item))}", font=font, fill='black')
        y += 37

    # REMINDER TO MAKE TEXT DRAW FUNCTION 
    if disaster_type == "Typhoon":
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
