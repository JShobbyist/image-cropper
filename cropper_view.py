# from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooser
import os
from kivy.lang import Builder
from kivy.properties import ListProperty

class CropperLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CropperLayout, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        # Window.clearcolor = (0.5, 0.5, 0.5, 1)
        
        left_side_panel = BoxLayout(orientation="vertical")
        self.add_widget(left_side_panel)
        info_panel = GridLayout(cols=2, size_hint_y=0.1)
        left_side_panel.add_widget(info_panel)
        self.image_widget = Image(size_hint_y=1)
        left_side_panel.add_widget(self.image_widget)


        info_panel.add_widget(Label(text='Cropped image width:'))
        self.final_img_width = Label(text='100')
        info_panel.add_widget(self.final_img_width)

        info_panel.add_widget(Label(text='Cropped image height:'))
        self.final_img_height = Label(text='100')
        info_panel.add_widget(self.final_img_height)

        
        side_panel = BoxLayout(orientation="vertical", size_hint_y = 0.8)
        side_panel.spacing = 20
        self.add_widget(side_panel)

        final_image_size_box = BoxLayout(orientation="vertical", padding=(0.30), size_hint_y=2)
        side_panel.add_widget(final_image_size_box)
        final_image_size_box.add_widget(Label(text="Select size of cropped image", size_hint_y=0.2))

        final_image_size_grid = GridLayout(cols=2)
        final_image_size_box.add_widget(final_image_size_grid)
        final_image_size_grid.add_widget(Label(text='Width:'))
        self.final_width = SizeTextInput(text='100', dimension='width')
        final_image_size_grid.add_widget(self.final_width)
        final_image_size_grid.add_widget(Label(text='Height:'))
        self.final_height = SizeTextInput(text='100', dimension='height')
        final_image_size_grid.add_widget(self.final_height)



        aspect_ratio_panel = GridLayout(cols=2)
        side_panel.add_widget(aspect_ratio_panel)

        aspect_ratio_panel.add_widget(Label(text='Select aspect ratio:', size_hint_y=2))
        self.aspect_ratio_field = TextInput(text='', multiline=False)
        aspect_ratio_panel.add_widget(self.aspect_ratio_field)
        aspect_ratio_panel.add_widget(Label(text='Lock aspect ratio:'))
        self.mylab = MyCheckBox()
        self.mylab.rgba = [1, 1, 1, 1]
        self.locked_aspect_ratio_checkbox = self.mylab
        aspect_ratio_panel.add_widget(self.locked_aspect_ratio_checkbox)

        width_panel = BoxLayout(orientation="vertical", size_hint_y=2)
        side_panel.add_widget(width_panel)

        width_info = BoxLayout(orientation="horizontal")
        width_panel.add_widget(width_info)
        # width_info.size_hint = 1, 0.15

        curr_width = Label(text="Crop area width (pixels):")
        width_info.add_widget(curr_width)
        self.width_field = SizeTextInput(text="100", dimension='width')
        width_info.add_widget(self.width_field)

        self.width_buttons = GridLayout(cols=3)
        width_panel.add_widget(self.width_buttons)
        w_plus_one = CropAreaButton(text='+1', dimension='width', value=1)
        w_plus_ten = CropAreaButton(text='+10', dimension='width', value=10)
        w_plus_hundred = CropAreaButton(text='+100', dimension='width', value=100)
        w_minus_one = CropAreaButton(text='-1', dimension='width', value=-1)
        w_minus_ten = CropAreaButton(text='-10', dimension='width', value=-10)
        w_minus_hundred = CropAreaButton(text='-100', dimension='width', value=-100)
        [self.width_buttons.add_widget(widget) for widget in (
            w_plus_one, w_plus_ten, w_plus_hundred,
            w_minus_one, w_minus_ten, w_minus_hundred
        )]

        height_panel = BoxLayout(orientation="vertical", size_hint_y=2)
        side_panel.add_widget(height_panel)

        height_info = BoxLayout(orientation="horizontal")
        height_panel.add_widget(height_info)
        
        curr_height = Label(text="Crop area height (pixels):")
        height_info.add_widget(curr_height)
        self.height_field = SizeTextInput(text="100", dimension='height')
        height_info.add_widget(self.height_field)
        
        self.height_buttons = GridLayout(cols=3)
        height_panel.add_widget(self.height_buttons)
        h_plus_one = CropAreaButton(text='+1', dimension='height', value=1)
        h_plus_ten = CropAreaButton(text='+10', dimension='height', value=10)
        h_plus_hundred = CropAreaButton(text='+100', dimension='height', value=100)
        h_minus_one = CropAreaButton(text='-1', dimension='height', value=-1)
        h_minus_ten = CropAreaButton(text='-10', dimension='height', value=-10)
        h_minus_hundred = CropAreaButton(text='-100', dimension='height', value=-100)
        [self.height_buttons.add_widget(widget) for widget in (
            h_plus_one, h_plus_ten, h_plus_hundred,
            h_minus_one, h_minus_ten, h_minus_hundred
        )]


        self.nxt = Button(text='Crop and save')
        # nxt.bind(on_press=self.next_image)
        # nxt.size_hint = 1, 1
        side_panel.add_widget(self.nxt)

        # rectangle_outline(self.canvas, (300, 300), (330, 330))

# Draw rectangle outline
def draw_rectangle_outline(canvas, bottom_left, top_right):
    with canvas:
        Color(255, 0, 0)
        bottom_right = top_right[0], bottom_left[1]
        top_left = bottom_left[0], top_right[1]
        Line(points=[
                bottom_left + bottom_right + top_right + top_left + bottom_left
            ], width=2, group='crop_rectangle')

class CropAreaButton(Button):
    def __init__(self, text, dimension, value):
        super().__init__(text=text)
        self.dimension = dimension
        self.value = value

class SizeTextInput(TextInput):
    def __init__(self, text, dimension):
        super().__init__(text=text, multiline=False)
        self.dimension = dimension

class MyCheckBox(CheckBox):
	rgba = ListProperty([1, 1, 1, 1])

Builder.load_file('mycheckbox.kv')

# class MyImage(Image):
#     def on_touch_up(self, touch):
#         if self.collide_point(*touch.pos):
#             p = img_click_pos(self.norm_image_size, self.size, touch.pos)
#             print(f'Relative image click position: {p}\n')
#             # print(touch)
#             # print(f'Box coordinates: {touch.pos}\n')
#             # print(f'Box size: {self.size}\n')
#             # print(f'Normalized img size: {self.norm_image_size}\n')
#             # print(f'Img ratio size: {self.image_ratio}\n')
