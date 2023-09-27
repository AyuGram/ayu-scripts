import os

from PIL import Image


def convert_image(root, filename):
    with Image.open(os.path.join(root, filename)) as img:
        img = img.convert("RGBA")
        resized_img = img.resize((232, 232))
        final_img = Image.new("RGBA", (256, 256), (255, 255, 255, 0))

        position = (12, 12)
        final_img.paste(resized_img, position, resized_img)

        final_img.save(os.path.join(root, "app_preview.png"))

        img.save(os.path.join(root, "app_icon.ico"), format="ICO", sizes=[(256, 256)])

        relative_path = os.path.relpath(root, '.')
        print(f'<file alias="art/ayu/{relative_path}/app.png">../../art/ayu/{relative_path}/app.png</file>')
        print(
            f'<file alias="art/ayu/{relative_path}/app_preview.png">../../art/ayu/{relative_path}/app_preview.png</file>')
        print(f'<file alias="art/ayu/{relative_path}/app_icon.ico">../../art/ayu/{relative_path}/app_icon.ico</file>')


for root, dirs, files in os.walk('.'):
    if "app.png" in files:
        convert_image(root, "app.png")
