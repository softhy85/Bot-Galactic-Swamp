from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from io import BytesIO
import os
import base64
directory_name: str = os.path.dirname(__file__)


def remove_transparent(pil_img) -> Image:
    color = (0, 0, 0, 255)
    pil_img.convert('RGBA')
    palette = pil_img.getpalette()
    for x in range(0, pil_img.size[0]):
        for y in range(0, pil_img.size[1]):
            seed = (x, y)
            pixel = pil_img.getpixel(seed)
            if isinstance(pixel, int):
                return pil_img
            if pixel[3] == 0:
                ImageDraw.floodfill(pil_img, seed, color, thresh=100)
    return pil_img


def mask_circle_transparent(size, blur_radius, offset=0) -> Image:

    offset = blur_radius * 2 + offset
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, size[0] - offset, size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    return mask


def arrived_image(username: str, icon_data: BytesIO):
    return_image: Image = Image.open(str(directory_name + "\\Swamp.png").replace("\\", "/"))
    icon_img = Image.open(icon_data)
    icon_img.convert('RGBA')
    icon_img = remove_transparent(icon_img)
    mask = mask_circle_transparent(icon_img.size, 0)
    icon_cropped = icon_img.copy()
    icon_cropped.putalpha(mask)

    icon_cropped.convert('RGBA')
    return_image.paste(icon_cropped, (50, 100), mask)

    draw_image = ImageDraw.Draw(return_image)
    title_font = ImageFont.truetype(str(directory_name + '\\Happy Sushi.ttf').replace("\\", "/"), 100)
    text: str = username
    if len(text) >= 10:
        text = username[0:7] + "..."
    draw_image.text((310, 150), text, (198, 241, 83), font=title_font)

    image_binary = BytesIO()
    return_image.save(image_binary, format="PNG")
    image_binary.seek(0)
    return image_binary

def leave_image(username: str, icon_data: BytesIO):
    return_image: Image = Image.open(str(directory_name + "\\Swamp.png").replace("\\", "/"))
    return_image.convert('RGBA')
    icon_img = Image.open(icon_data)
    icon_img.convert('RGBA')
    icon_img = remove_transparent(icon_img)
    mask = mask_circle_transparent(icon_img.size, 0)
    icon_cropped = icon_img.copy()
    icon_cropped.putalpha(mask)
    icon_cropped.convert('RGBA')
    return_image.paste(icon_cropped, (50, 100), mask)

    draw_image = ImageDraw.Draw(return_image)
    title_font = ImageFont.truetype(str(directory_name + '\\Happy Sushi.ttf').replace("\\", "/"), 100)
    text: str = username
    if len(text) >= 10:
        text = username[0:7] + "..."
    draw_image.text((310, 150), text, (198, 241, 83), font=title_font)
    return_image = ImageEnhance.Color(return_image).enhance(0.1)
    image_binary = BytesIO()
    return_image.save(image_binary, format="PNG")
    image_binary.seek(0)
    return image_binary


if __name__ == '__main__':
    image: Image = leave_image("Test Test Test Test", str(directory_name + "\\worker.png").replace("\\", "/"))
