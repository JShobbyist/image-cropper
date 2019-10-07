import PIL
import sys
from kivy.app import App
from kivy.core.window import Window
from functools import partial

import config
from cropper_view import CropperLayout
from cropper_model import (Cropper, get_imgs, on_image_click,
    clear_click_pos, on_crop_area_resize, get_aspect_ratio_from_str)

class MyApp(App):
    def __init__(self, imgs_data, **kwargs):
        super().__init__(**kwargs)
        self.imgs_data = imgs_data
        self.cropper = None
        self.layout = CropperLayout()
        self.crop_and_load_next()
        # self.layout.nxt.on_press = lambda x:self.crop_and_load_next()
        self.layout.nxt.bind(on_press=lambda x:self.crop_and_load_next())
        

    def build(self):
        self.title = 'Image cropper'
        # layout = CropperLayout()
        return self.layout
    
    def crop_and_load_next(self):
        # If current image is not the first image and it has no
        # selected crop area, don't do anything
        if self.cropper and (self.cropper.crop() is False):
            return

        # Exit program after cropping last image
        try:
            orig_img, orig_format, orig_name = self.imgs_data.pop(0)
        except IndexError:
            sys.exit()
        
        if not self.cropper:
            self.cropper = Cropper(
                orig_img=orig_img, orig_format=orig_format, orig_name=orig_name
            )
            Window.bind(on_resize=lambda x,y,z:clear_click_pos(self.layout.image_widget, self.cropper))
            self.layout.aspect_ratio_field.text = str(self.cropper.aspect_ratio)
            self.layout.aspect_ratio_field.bind(text=partial(new_aspect_ratio, self.cropper))

            for btn in (
                self.layout.width_buttons.children + self.layout.height_buttons.children
            ):
                btn.bind(on_press=partial(
                    change_dimension, btn.dimension, btn.value, self.cropper, self.layout)
                )

            self.layout.image_widget.on_touch_up = (
                lambda touch:on_image_click(
                    touch, self.layout.image_widget, self.cropper
                )
            )
            self.layout.locked_aspect_ratio_checkbox.bind(
                active=partial(lock_aspect_ratio, self.cropper)
            )
            for size_input in (self.layout.width_field, self.layout.height_field):
                size_input.bind(text=partial(
                    set_dimension, size_input.dimension, self.cropper, self.layout
                ))
            
            for final_size in (self.layout.final_width, self.layout.final_height):
                final_size.bind(text=partial(
                    set_final_size_dimension, final_size.dimension, self.cropper,
                    self.layout
                ))
        else:
            self.cropper.orig_img = orig_img
            self.cropper.orig_format = orig_format
            self.cropper.orig_name = orig_name
            print(f'Current image: {self.cropper.orig_name}, {self.cropper.orig_img}')
            # old_width = self.cropper.width
            # old_height = self.cropper.height
            # old_aspect_ratio = self.cropper.aspect_ratio
            # old_locked_aspect_ratio = self.cropper.locked_aspect_ratio
            # self.cropper = Cropper(
            #     orig_img=orig_img, orig_format=orig_format, orig_name=orig_name,
            #     width=old_width, height=old_height, aspect_ratio=old_aspect_ratio,
            #     locked_aspect_ratio=old_locked_aspect_ratio
            # )
        clear_click_pos(self.layout.image_widget, self.cropper)
        self.layout.image_widget.source = self.cropper.orig_image_full_path()
        self.layout.image_widget.reload()


def change_dimension(dimension, change_amount, cropper, cropper_layout, _):
    print('\nClicked!\n')
    current_value = cropper.width if dimension == 'width' else cropper.height
    cropper.set_side(dimension, current_value + change_amount)
    on_crop_area_resize(cropper_layout.image_widget, cropper)
    cropper_layout.width_field.text = str(round(cropper.width))
    cropper_layout.height_field.text = str(round(cropper.height))

# def set_dimension(*args):
#     print(f'Args: {args}')

def set_dimension(dimension, cropper, cropper_layout, instance, _):
    value_str = instance.text
    if not value_str.isdigit():
        return
    print(f'value_str is {value_str}')
    value = int(value_str)
    print(f'Value is {value}')
    cropper.set_side(dimension, value)
    on_crop_area_resize(cropper_layout.image_widget, cropper)
    cropper_layout.width_field.text = str(round(cropper.width))
    cropper_layout.height_field.text = str(round(cropper.height))

def set_final_size_dimension(dimension, cropper, cropper_layout, instance, value):
    if not value.isdigit():
        return
    print('Running set_final_size_dimension')
    cropper.set_final_side(dimension, value)
    cropper_layout.final_img_width.text = str(cropper.final_width)
    cropper_layout.final_img_height.text = str(cropper.final_height)
    

def lock_aspect_ratio(cropper, checkbox, locked):
    cropper.locked_aspect_ratio = locked

def new_aspect_ratio(cropper, textinput, _):
    new_ratio = textinput.text
    print(f'Running new_aspect_ratio. New ratio: {new_ratio}')
    cropper.aspect_ratio = get_aspect_ratio_from_str(new_ratio)
    print(f'Cropper.aspect_ratio: {cropper.aspect_ratio}')


if __name__ == '__main__':
    imgs_data = get_imgs('Input images')
    if len(imgs_data) < 1:
        print('No images were found inside the folder "Input images"')
        input()
        sys.exit()
    MyApp(imgs_data).run()



# def next_image(self, obj):
#     self.image_widget.source='Input images/1.png'