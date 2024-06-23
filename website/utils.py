import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils.translation import gettext as trans

def checklist_image(checklist, disaster_type, facts):
    # Creates the background image for the printable checklist
    image = Image.new('RGB', (900, 600), color='white')
    draw = ImageDraw.Draw(image)
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'NotoSansJP-VariableFont_wght.ttf')
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    # Position and creation of disaster name
    x, y = 450, 10
    draw.text((x, y), trans(disaster_type), font=font, fill='black')

    # Printing out the checklist line by line
    x, y = 10, 30

    for item in checklist:
        draw.text((x, y), f"- {trans(item)}", font=font, fill='black')
        y += 20

    x, y = 700, 30

    for item in facts:
        draw.text((x, y), f"- {trans(item)}", font=font, fill='black')
        y += 20

    # Naming and saving file to static folder
    image_filename = 'disaster_poster.png'
    image_path = os.path.join(settings.STATIC_ROOT, 'images', image_filename)
    image.save(image_path)

    return image_filename
