import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext, get_language
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from gtts import gTTS

def parse_furigana(text: str) -> tuple[str, list[tuple[str, str]]]:
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')
    matches = ruby_pattern.findall(text)
    parsed_text = []
    for match in matches:
        base_text, furigana = match
        parsed_text.append((base_text, furigana))
        text = text.replace(f'<ruby>{base_text}<rt>{furigana}</rt></ruby>', base_text)
    return text, parsed_text

def remove_furigana(text: str) -> str:
    ruby_pattern = re.compile(r'<ruby>(.*?)<rt>.*?</rt></ruby>')
    cleaned_text = ruby_pattern.sub(r'\1', text)
    return cleaned_text

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
            draw_text(draw, gettext(item), text_font, x + int(40 * scale), y + int(27 * scale))

            if not bigList:
                y += int(46 * scale)

            else:
                y += int(42 * scale)
        else:
            draw_text(draw, gettext(item), text_font, x + int(40 * scale), y + int(6 * scale))

            if not bigList:
                y += int(22 * scale)

            else:
                y += int(9 * scale)
    return y

def typhoon_flood_checklist(draw, fonts, scale, user, disaster_type):

    header_font = fonts['header']
    draw_text(draw, gettext("Typhoons come with"), header_font, 230 * scale, 220 * scale)
    draw_text(draw, gettext("rains, floods, landslides"), header_font, 230 * scale, 260 * scale)

    level1_typhoon = [
        (gettext("Check a hazard map"), True),
        (gettext("Find evacuation centers"), True),
        (gettext("Check items on checklist"), True),
        (gettext("Beware of falling things in your"), True),
        (gettext("house"), False),
    ]
    
    level2_typhoon = [
        (gettext("Decide on evacuation center"), True),
        (gettext("Recheck emergency bags"), True),
        (gettext("Prepare for power outage"), True),
    ]
    
    if user.child_bool:
        level3_typhoon = [
            (gettext("Elderly, people with disabilities, and"), True),
            (gettext("families with children must evacuate"), False),
        ]
    
    else:
        level3_typhoon = [
            (gettext("Elderly & people with disabilities"), True),
            (gettext("must evacuate"), False),
        ]
    
    level4_typhoon = [
        (gettext("Go to an evacuation center"), True),
        (gettext("immediately"), False),
    ]
    
    level5_typhoon = [
        (gettext("Save your life!"), True),
    ]
    
    if disaster_type == "Typhoon":
        disaster_tips = [
            (gettext("Check your house before leaving (window, breaker,"), True),
            (gettext("gas valve)"), False),
            (gettext("Check yourself and your belongings"), True),
            (gettext("Follow the route avoiding dangerous areas"), True),
            (gettext("While evacuating, watch out for flooding"), True),
            (gettext("If you can't evacuate safely, stay inside and go to"), True),
            (gettext("the highest floor"), False),
        ]

    else:
        disaster_tips = [
            (gettext("Close all windows in your house and make sure"), True),
            (gettext("anything outside is moved indoors"), False),
            (gettext("Be aware of strong winds as they will make things fly"), True),
            (gettext("Avoid places with high water levels (50 cm or higher)"), True),
            (gettext("Watch out for manholes, gutters, and irrigation canals"), True),
            (gettext("If you can't evacuate safely, stay inside and go to"), True),
            (gettext("the highest floor"), False),
        ]

    if user.blind_bool or user.deaf_bool or user.wheelchair_bool:
        disaster_tips.append((gettext("Register people who need evacuation support"), True))

    if user.child_bool or user.baby_bool:
        disaster_tips.append((gettext("Don't use a baby stroller"), True))
        disaster_tips.append((gettext("Use a backpack and always hold your children's hand"), True))

    if user.pet_bool:
        disaster_tips.append((gettext("Use a lead, cage, and carry bag during evacuation"), True))
        disaster_tips.append((gettext("Keep pets calm so they don't panic"), True))
        
    y = bullet_spacing(draw, fonts, level1_typhoon, 145 * scale, 328 * scale, scale)
    y = bullet_spacing(draw, fonts, level2_typhoon, 145 * scale, y + int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_typhoon, 145 * scale, y + int(40 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_typhoon, 145 * scale, y + int(40 * scale), scale)
    bullet_spacing(draw, fonts, level5_typhoon, 145 * scale, y + int(60 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, gettext("Evacuation Guideline"), guideline_font, 850 * scale, 1020 * scale)

    # Writing checklist items to a text file for tts to read
    with open("website/static/typhoon_tts.txt", "a", encoding="utf-8") as file:
        file.write(gettext("Levels of typhoon preparedness:\n"))


        def write_level(file, level_num, items):
            file.write(gettext("In a level %(level_num)s typhoon:\n") % {'level_num': level_num})
            full_items = []
            for item, is_new in items:
                if is_new:
                    if full_items:
                        full_items.append(full_items.pop() + ",")
                    full_items.append(item)
                else:
                    full_items[-1] += " " + item
            if full_items:
                file.write(", ".join(full_items) + ",\n")

        write_level(file, "1", level1_typhoon)
        write_level(file, "2", level2_typhoon)
        write_level(file, "3", level3_typhoon)
        write_level(file, "4", level4_typhoon)
        write_level(file, "5", level5_typhoon)

        file.write(gettext("Some general typhoon tips are:\n"))
        full_tips = []
        for item, is_new in disaster_tips:
            if is_new:
                if full_tips:
                    full_tips.append(full_tips.pop() + ",")
                full_tips.append(item)
            else:
                full_tips[-1] += " " + item
        if full_tips:
            file.write(",\n".join(full_tips) + ",\n")

    if len(disaster_tips) > 11:
        bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale, True)
    
    else:
        bullet_spacing(draw, fonts, disaster_tips, 700 * scale, 1050 * scale, scale)

def earthquake_checklist(draw, fonts, scale):

    header_font = fonts['header']
    draw_text(draw, gettext("During an earthquake,"), header_font, 230 * scale, 220 * scale)
    draw_text(draw, gettext("follow these safety steps:"), header_font, 230 * scale, 260 * scale)

#information from https://www.jma.go.jp/jma/en/Activities/inttable.html
    level0_earthquake = [
        (gettext("Imperceptible to people, but recorded"), True),
        (gettext("by seismometers"), False),
    ]

    level1_earthquake = [
        (gettext("Felt slightly by some people keeping quiet"), True),
        (gettext("in buildings"), False),
    ]

    level2_earthquake = [
        (gettext("Felt by many people keeping quiet in"), True),
        (gettext("buildings"), False),
        (gettext("Hanging objects swing slightly"), True),
    ]

    level3_earthquake = [
        (gettext("Felt by most people in buildings and some"), True),
        (gettext("walking"), False),
        (gettext("Dishes rattle and electric wires swing."), True),
    ]

    level4_earthquake = [
        (gettext("Hanging objects swing significantly"), True),
        (gettext("Unstable ornaments may fall and electric"), True),
        (gettext("wires swing significantly"), False),
    ]

    level5_earthquake = [
        (gettext("Unsecured furniture may move and fall"), True),
        (gettext("Windows may break and roads may sustain"), True),
        (gettext("damage, and some walls may collapse"), False),
    ]

    level6_earthquake = [
        (gettext("Unsecured furniture moves and may topple"), True),
        (gettext("Impossible to stand or move without crawling"), True),
        (gettext("Walls may collapse"), True),
    ]

    level7_earthquake = [
        (gettext("Most furniture topples; reinforced walls may"), True),
        (gettext("collapse"), False),
    ]

    # information from https://www.kcif.or.jp/web/en/livingguide/emergency/
    disaster_tips = [
        (gettext("Ensure Safety: Stay calm and prioritize your"), True),
        (gettext("safety"), False),
        (gettext("Turn Off Utilities: Alert others and turn off gas"), True),
        (gettext("and electricity immediately"), False),
        (gettext("Secure an Exit: Open doors and windows if"), True),
        (gettext("jammed to create an escape route"), False),
        (gettext("Handle Fires: Shout for help and extinguish"), True),
        (gettext("small fires immediately"), False),
        (gettext("Avoid Rush: Exit carefully, watch for"), True),
        (gettext("falling debris"), False),
        (gettext("Stay Clear of Hazards: Avoid narrow alleys,"), True),
        (gettext("cliffs, and rivers; watch for falling objects"), False),
        (gettext("Watch for Aftershocks: Prepare for landslides"), True),
        (gettext("or tsunamis if near mountains or the sea"), False),
        (gettext("Evacuate on Foot: Go to the nearest shelter with"), True),
        (gettext("minimal belongings"), False),
        (gettext("Help Others: Assist the elderly, disabled,"), True),
        (gettext("and injured"), False),
        (gettext("Get Accurate Info: Follow reliable sources for"), True),
        (gettext("updates and watch out for aftershocks"), False),
    ]

    # Writing checklist items to a text file for tts to read
    with open("website/static/earthquake_tts.txt", "a", encoding="utf-8") as file:
        file.write(gettext("Levels of earthquakes:\n"))


        def write_level(file, level_num, items):
            file.write(gettext("In a level %(level_num)s earthquake:\n") % {'level_num': level_num})
            full_items = []
            for item, is_new in items:
                if is_new:
                    if full_items:
                        full_items.append(full_items.pop() + ",")
                    full_items.append(item)
                else:
                    full_items[-1] += " " + item
            if full_items:
                file.write(", ".join(full_items) + ",\n")

        write_level(file, "level 0", level0_earthquake)
        write_level(file, "level 1", level1_earthquake)
        write_level(file, "level 2", level2_earthquake)
        write_level(file, "level 3", level3_earthquake)
        write_level(file, "level 4", level4_earthquake)
        write_level(file, "level 5", level5_earthquake)
        write_level(file, "level 6", level6_earthquake)
        write_level(file, "level 7", level7_earthquake)

        file.write("Some general earthquake tips are:\n")
        full_tips = []
        for item, is_new in disaster_tips:
            if is_new:
                if full_tips:
                    full_tips.append(full_tips.pop() + ",")
                full_tips.append(item)
            else:
                full_tips[-1] += " " + item
        if full_tips:
            file.write(",\n".join(full_tips) + ",\n")

    y = bullet_spacing(draw, fonts, level0_earthquake, 810 * scale, 1050 * scale, scale)
    y = bullet_spacing(draw, fonts, level1_earthquake, 810 * scale, y + int(35 * scale), scale)
    y = bullet_spacing(draw, fonts, level2_earthquake, 810 * scale, y + int(15 * scale), scale)
    y = bullet_spacing(draw, fonts, level3_earthquake, 810 * scale, y - int(2 * scale), scale)
    y = bullet_spacing(draw, fonts, level4_earthquake, 810 * scale, y - int(2 * scale), scale)
    y = bullet_spacing(draw, fonts, level5_earthquake, 810 * scale, y - int(10 * scale), scale)
    y = bullet_spacing(draw, fonts, level6_earthquake, 810 * scale, y - int(10 * scale), scale)
    bullet_spacing(draw, fonts, level7_earthquake, 810 * scale, y + int(8 * scale), scale)

    guideline_font = fonts['guideline']
    draw_text(draw, gettext("Safety Guidelines"), guideline_font, 210 * scale, 328 * scale)
    bullet_spacing(draw, fonts, disaster_tips, 55 * scale, 368 * scale, scale)

def checklist_image(checklist, disaster_type, user):
    if disaster_type == "Typhoon":
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
    # Append the title to the appropriate text file
    with open(f"website/static/{disaster_type.lower()}_tts.txt", "w", encoding="utf-8") as file:
        big_header = ""
        if disaster_type == "Earthquake":
            big_header = f"{user.name}様への地震ポスター\n" if get_language().startswith("jp") else "Your Poster for Earthquakes\n"
        else:
            big_header = f"{user.name}様への台風ポスター\n" if get_language().startswith("jp") else "Your Poster for Typhoons\n"
        file.write(big_header)
        file.write(gettext("Items to prepare:,\n"))

        if get_language().startswith("jp"):
            for item in checklist[gettext("Go Bag")]:
                file.write(f"{remove_furigana(item)},\n")
        else:
            for item in checklist[gettext("Go Bag")]:
                file.write(f"{item},\n")

    if disaster_type == "Earthquake":
        big_header = f"{user.name}様への地震ポスター" if get_language().startswith("jp") else "Your Poster for Earthquakes"
        tasks.append((draw_text, (draw, gettext("Your Poster for Earthquakes"), fonts['title'], 190 * scale, 35 * scale)))
    
    else:
        big_header = f"{user.name}様への台風ポスター" if get_language().startswith("jp") else "Your Poster for Typhoons"
        tasks.append((draw_text, (draw, big_header, fonts['title'], 320 * scale, 50 * scale)))

    date_offset = 400 if not get_language().startswith("jp") else 290
    if disaster_type == "Earthquake":
        date_offset -= 70 if get_language().startswith("jp") else 100

    tasks.append((draw_text, (draw, gettext("Created by S.E.E.L.E on %(date)s") % {"date": datetime.now().date()}, fonts['info'], date_offset * scale, 140 * scale)))
    tasks.append((draw_text, (draw, gettext("Items to prepare"), fonts['header'], 900 * scale, 220 * scale)))

    y = 310 * scale

    if get_language().startswith("jp"):
        for i, item in enumerate(checklist[gettext("Go Bag")]):
            x = 735 * scale
            tasks.append((draw_text, (draw, f"□ {remove_furigana(item)}", fonts['items'], x, y)))
            y += 37 * scale
    else:
        for i, item in enumerate(checklist[gettext("Go Bag")]):
            x = 740 * scale
            tasks.append((draw_text, (draw, f"□ {item}", fonts['items'], x, y)))
            y += 37 * scale

    if disaster_type == "Typhoon":
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

def tts_execute(disaster_type):
    FLIST = open(f"website/static/{disaster_type.lower()}_tts.txt", "r").read().replace("\n", " ")
    #print("please wait...processing")
    TTS = gTTS(text=str(FLIST), lang='en-us')

    file_path = os.path.join(settings.STATIC_ROOT, 'voice.mp3')
    TTS.save(file_path)