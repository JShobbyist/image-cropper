import config
import os
from PIL import Image, ImageDraw
from cropper_view import draw_rectangle_outline

class Cropper:
    def __init__(self, orig_img, orig_format, orig_name, width=100, height=100, locked_aspect_ratio=False, aspect_ratio=None):
        # self.img_and_format = img_and_format
        self.orig_img = orig_img
        self.orig_format = orig_format
        self.orig_name = orig_name
        # self.image = None
        self.final_width = 100
        self.final_height = 100

        self.width = width
        self.height = height
        self.locked_aspect_ratio = False
        if locked_aspect_ratio:
            self.locked_aspect_ratio = locked_aspect_ratio
        self.aspect_ratio = 1
        if aspect_ratio:
            self.aspect_ratio = aspect_ratio
        self.click_pos = None
        self.last_kivy_click_pos = None
        # self.update_image()

    def orig_image_full_path(self):
        return f'{config.INPUT_IMG_DIRECTORY}/{self.orig_name}.{self.orig_format}'

    # def temp_image_full_path(self):
    #     return f'{config.TEMP_IMG_DIRECTORY}/temp.{self.orig_format}'
    
    def output_image_full_path(self):
        return f'{config.OUTPUT_IMG_DIRECTORY}/{self.orig_name}.{self.orig_format}'

    def set_side(self, side, value):
        sides = ['width', 'height']
        if side not in sides:
            return False
        value = max(1, value)
        # print(f'\nRunning set_side. Side is {side}, value is {value}\n')
        if side == 'width':
            self.width = value
            if self.aspect_ratio and self.locked_aspect_ratio:
                # print('\nLOCKED ASPECT RATIO\n')
                self.height = max(1, value/self.aspect_ratio)
        else:
            self.height = value
            if self.aspect_ratio and self.locked_aspect_ratio:
                # print('\nLOCKED ASPECT RATIO\n')
                self.width = max(1, value * self.aspect_ratio)

    def set_final_side(self, side, value):
        sides = ['width', 'height']
        if side not in sides:
            return False
        try:
            value = max(1, int(value))
        except ValueError:
            return False
        # print(f'\nRunning set_side. Side is {side}, value is {value}\n')
        if side == 'width':
            self.final_width = value
        else:
            self.final_height = value


    @property
    def orig_img(self):
        return self.__orig_img

    @orig_img.setter
    def orig_img(self, new_img):
        self.__orig_img = new_img
        self.click_pos = None

    # # Add crop rectangle to image, if appropriate
    # # (i.e. if self.click_pos is not None)
    # def update_image(self):
    #     img = self.orig_img.copy()
    #     if self.click_pos is not None:
    #         crop_area = pil_crop_area(self.click_pos, (self.width, self.height), img.size)
    #         print(f'\n\n\nUpdate crop_area: {crop_area}\n\n\n')
    #         draw = ImageDraw.Draw(img) 
    #         draw.rectangle(crop_area, fill=None, outline='red')
    #         del draw
    #     self.image = img
    #     img.save(self.temp_image_full_path())
    
    def crop(self):
        img = self.orig_img.copy()
        if self.click_pos is not None:
            crop_area = pil_crop_area(self.click_pos, (self.width, self.height), img.size)
            cropped_img = img.crop(box=crop_area)
            resized_cropped_img = cropped_img.resize(
                (self.final_width, self.final_height),
                Image.ANTIALIAS
            )
            resized_cropped_img.save(self.output_image_full_path(), quality=100)
            return True
        return False

    @property
    def aspect_ratio(self):
        return self.__aspect_ratio
    
    @aspect_ratio.setter
    def aspect_ratio(self, value):
        try:
            if value > 0:
                self.__aspect_ratio = value
                return True
        except (TypeError, ValueError):
            pass
        return False

    @property
    def locked_aspect_ratio(self):
        return self.__locked_aspect_ratio

    @locked_aspect_ratio.setter
    def locked_aspect_ratio(self, locked):
        self.__locked_aspect_ratio = bool(locked)
        

# Returns none if string is invalid
def get_aspect_ratio_from_str(string):
    try:
        if ':' not in string:
            return float(string)
        width, height = string.split(':')
        width, height = float(width), float(height)
        return width/height
    except (TypeError, ValueError, AttributeError):
        return None

# def validate_size_length(size):
#     try:
#         if size >= 1:
#             return True
#     except TypeError:
#         pass
#     return False

# Function responsible for loading all the images file
# contained inside a given directory.
# Returns list of tuples (Pil.Image, img_format, img_name)
def get_imgs(folder_name):
    try:
        imgs = [
            (Image.open(f'{folder_name}/{img_path}'), img_path)
            for img_path in os.listdir(folder_name)
            if not img_path.endswith('.db')
        ]
        return [
            (img_file, img_path.rsplit('.', 1)[1], img_path.rsplit('.', 1)[0])
            for img_file, img_path in imgs
        ]
    except FileNotFoundError:
        return []

# Calculate click position relative to image
# Returns value between 0, 0 and 1, 1
# 0, 0 is lower left corner of image
def img_click_pos(img_size, box_size, click_pos):
    box_center = box_size[0]/2, box_size[1]/2
    # The image's 0, 0 point; relative to the Box
    img_start = box_center[0] - (img_size[0]/2), box_center[1] - (img_size[1]/2)
    relative_click_pos = click_pos[0] - img_start[0], click_pos[1] - img_start[1]

    # Proportionally reduce the relative click position
    # to a number between 0 and 1
    relative_click_pos = [
        coord/img_size[index]
        for index, coord in enumerate(relative_click_pos)
    ]

    # Constrain the relative_click_pos coordinates to 0 and 1
    relative_click_pos = [
        max(0, min(coord, 1))
        for coord in relative_click_pos
    ]
    
    return tuple(relative_click_pos)

# Function that will be monkey patched to Image widget's on_touch_up method
# Will run every time the image is clicked on
def on_image_click(touch, img_widget, cropper):
    if img_widget.collide_point(*touch.pos):
        cropper.click_pos = img_click_pos(
            img_widget.norm_image_size, img_widget.size, touch.pos
        )
        draw_crop_area_rectangle(touch.pos, img_widget, cropper)
        

def on_crop_area_resize(img_widget, cropper):
    if cropper.last_kivy_click_pos:
        draw_crop_area_rectangle(cropper.last_kivy_click_pos, img_widget, cropper)

def clear_click_pos(img_widget, cropper):
    cropper.last_kivy_click_pos = None
    cropper.click_pos = None
    img_widget.canvas.remove_group('crop_rectangle')

def draw_crop_area_rectangle(pos, img_widget, cropper):
    source_img_size = cropper.orig_img.size
    # Scale factor. Example: 0.2 (20%)
    scale_factor = max(
        img_widget.norm_image_size[0]/source_img_size[0],
        img_widget.norm_image_size[1]/source_img_size[1]
    )
    x_dist = (cropper.width * scale_factor)/2
    y_dist = (cropper.height * scale_factor)/2
    bottom_left = (pos[0]-x_dist, pos[1]-y_dist)
    top_right = (pos[0]+x_dist, pos[1]+y_dist)
    img_widget.canvas.remove_group('crop_rectangle')
    draw_rectangle_outline(img_widget.canvas, bottom_left, top_right)
    cropper.last_kivy_click_pos = pos

# # Function that will be monkey patched to Image widget's on_touch_up method
# # Will run every time the image is clicked on
# def on_image_click(touch, img_widget, cropper):
#     print(f'\n\n\nimg_widget: {img_widget};\ntouch:{touch}\ncropper:{cropper}\n')
#     if img_widget.collide_point(*touch.pos):
#         click_pos = img_click_pos(img_widget.norm_image_size, img_widget.size, touch.pos)
#         cropper.click_pos = click_pos
#         cropper.update_image()
#         img_widget.reload()
#         print(f'Relative image click position: {click_pos}\n')

"""
Calculates the box area needed for the PIL.Image.crop function
PIL Box=(left_x, upper_y, right_x, bottom_y).

Note that image_size is the size of the actual image file being
cropped; it's unrelated to the kivy.uix.Image object

click_pos ranges from (0, 0) to (1, 1), where 0, 0 is the bottom-left corner
crop_size and image_size are (width, height) tuples

Coordinates follow the Kivy coordinate system until the
end of the function, where they are converted to PIL coords
Coodinate systems:
Pillow coords: X, Y; with 0,0 being top-left corner
Kivy coords: X, Y;   with 0, 0 being bottom-left corner
"""
def pil_crop_area(click_pos, crop_size, image_size):
    print(f'''
    Running pil_crop_area
    click_pos: {click_pos}
    crop_size: {crop_size}
    image_size: {image_size}
    ''')

    image_width, image_height = image_size
    crop_width = min(crop_size[0], image_width)
    crop_height = min(crop_size[1], image_height)
    click_x =  click_pos[0] * image_width
    click_y =  click_pos[1] * image_height
    print(f'''
    image_width, image_height: {image_width}, {image_height}
    crop_width, crop_height: {crop_width}, {crop_height}
    click_x, click_y: {click_x}, {click_y}
    click_pos0, click_pos1: {click_pos[0]}, {click_pos[1]}
    ''')

    kivy_left_x = max(0, click_x - (crop_width/2))
    kivy_bottom_y = max(0, click_y - (crop_height/2))
    kivy_right_x = min(image_width-1, click_x + (crop_width/2))
    kivy_upper_y = min(image_height-1, click_y + (crop_height/2))
    print(f'''
    KIVY COORDS:
    Bottom left: {kivy_left_x, kivy_bottom_y}
    Upper right: {kivy_right_x, kivy_upper_y}
    ''')

    left_x = kivy_left_x
    right_x = kivy_right_x
    bottom_y = kivy_y_to_pil_y(kivy_bottom_y, image_height)
    upper_y = kivy_y_to_pil_y(kivy_upper_y, image_height)
    print(f'''
    PIL COORDS:
    Bottom left: {left_x, bottom_y}
    Upper right: {right_x, upper_y}
    ''')
    return int(left_x), int(upper_y), int(right_x), int(bottom_y)

def kivy_y_to_pil_y(y, height):
    return (height - 1) - y