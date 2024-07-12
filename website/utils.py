import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans
import re

def remove_furigana(text):
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    return ruby_pattern.sub(r'\1', text)

# Function that creates spacing for bullet points
def bullet_spacing(draw, font_path, list, x, y):
    for item, bullet_point in list:
        if bullet_point:
            # Adds the bullet point which needs to have a bigger font size than the text
            font_size = 55
            font = ImageFont.truetype(font_path, font_size)
            draw.text((x, y), f"\u2022", font=font, fill='black')

            # Adds the text
            font_size = 25
            font = ImageFont.truetype(font_path, font_size)
            x += 40
            y += 28
            draw.text((x, y), f"{trans(item)}", font=font, fill='black')
            x -= 40
            y += 18
        
        else:
            x += 40
            y += 6
            draw.text((x, y), f"{trans(item)}", font=font, fill='black')
            x -= 40
            y += 16

# Generates typhoon checklist
def typhoon_checklist(draw, font_path):
    font_size = 33
    font = ImageFont.truetype(font_path, font_size)
    x, y = 230, 220
    draw.text((x, y), "Typhoons come with", font=font, fill='black')
    x, y = 230, 260
    draw.text((x, y), "rains, floods, landslides", font=font, fill='black')

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
        ("Watch out for floods and landslides", True),
        ("Stay away from rivers, cliffs, and", True),
        ("slopes", False),
        ("Go to the highest floor of a", True),
        ("building", False),
    ]
    
    disaster_tips = [
        ("Store items that can easily fly away in your house in a", True),
        ("safe container", False),
        ("Prevent the windows in your house from breaking by", True),
        ("covering them and closing shutters", False),
        ("Watch out for signs of flooding or landslides", True),
        ("Signs of landslides: peebles falling from a slope, cracks", True),
        ("apperaring on a slope, water suddenly gushing out", False),
        ("from a slope, water in the river suddently decreasing,", False),
        ("and sounds of mountain rumbling or earth rumbling", False),
        ("If you notice any of the signs, immediately move away", True),
        ("from the cliff or slope", False),
        ("As a last case scenerio, go to the highest floor of a", True),
        ("building thats away from any cliffs or slopes", False)
    ]
    

    
    font_size = 25
    font = ImageFont.truetype(font_path, font_size)
    
    x, y = 145, 328
    bullet_spacing(draw, font_path, level1_typhoon, x, y)

    y += 220
    bullet_spacing(draw, font_path, level2_typhoon, x, y)

    y += 175
    bullet_spacing(draw, font_path, level3_typhoon, x, y)

    y += 100
    bullet_spacing(draw, font_path, level4_typhoon, x, y)

    y += 85
    bullet_spacing(draw, font_path, level5_typhoon, x, y)

    x, y = 880, 1025
    font_size = 37
    font = ImageFont.truetype(font_path, font_size)
    draw.text((x, y), "Evacuation Guideline", font=font, fill='black')

    x,y = 700, 1050
    bullet_spacing(draw, font_path, disaster_tips, x, y)


def checklist_image(checklist, disaster_type, facts):
    # Loading the image template from static folder
    background_path = os.path.join(settings.STATIC_ROOT, 'images', 'template.png')
    background = Image.open(background_path).convert('RGB')

    # Ensure the background image has the Japanese A4 paper size (1415 x 2000).
    background = background.resize((1415, 2000))

    draw = ImageDraw.Draw(background)

    # Position and creation of disaster name
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-VariableFont_wght.ttf')
    font_size = 65
    font = ImageFont.truetype(font_path, font_size)
    x, y = 260, 50
    draw.text((x, y), trans(f"Your checklist for {disaster_type}s"), font=font, fill='black')

    # date/time/username TEMPORARY
    font_size = 38
    font = ImageFont.truetype(font_path, font_size)
    x, y = 400, 140
    draw.text((x, y), "created by S.E.E.L.E date/time/username", font=font, fill='black')

    # Printing out the checklist line by line
    font_size = 37
    font = ImageFont.truetype(font_path, font_size)
    x, y = 900, 220
    draw.text((x, y), "Items to prepare", font=font, fill='black')

    font_size = 29
    font = ImageFont.truetype(font_path, font_size)
    x, y = 750, 310

    for item in checklist:
        draw.text((x, y), f"- {remove_furigana(trans(item))}", font=font, fill='black')
        y += 37

    # Calling function depending on disaster that creates the text for the poster
    if disaster_type == "Typhoon":
        typhoon_checklist(draw, font_path)

    # Naming and saving file to static folder
    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    background.save(image_path)

    return image_filename
