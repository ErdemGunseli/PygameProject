from colours import *
from strings import *
from abc import ABC, abstractmethod
from utils import *
import pygame

# TODO: !!! CREATE THEME/STYLE OBJECT THAT DEFAULT VALUES ARE OBTAINED FROM

# TODO: Integrate UI elements into game world.
#  Have an optional draw offset in draw methods.
#  Create sprites as usual, add relevant UI element into lists!

# TODO: Improve Slider and Progress Bar functionality - do not use so many rectangles as the position of the slider
#  should entirely be determined by its rectangle.
#  Make them like text where the position of the surface is calculated from the rect:
# TODO: SAME PROBLEM WITH TEXT BOX

# TODO: PADDING ISSUE WITH TEXT

# TODO: HOVER COLOURS SHOULD DEFAULT TO NONE, AND IF THEY ARE NONE, BE SET THE SAME AS THE NON-HOVER !!!!!!!!!

# TODO: RELATIONAL ALIGNMENT


"""
This is my own UI framework, providing a dynamic component library, layout management, and responsive rendering.
"""


# An abstract class which all the UI elements inherit from:
class View(ABC, pygame.sprite.Sprite):
    # When the frame (border / background) of the UI element should be shown:
    NEVER = 0
    ALWAYS = 1
    HOVER = 2
    FOCUS = 3

    # Text Alignment:
    CENTRE = 0
    LEFT = 1
    RIGHT = 2

    # Orientation
    HORIZONTAL = 0
    VERTICAL = 1

    """
    IMPORTANT: For attributes such as margin, padding, frame_thickness, corner_radius, font_size, etc.
    Their values are the proportion of the screen which they should occupy, since the game needs to be
    resolution independent, and passing those values as pixels would prevent this.
    (i.e. 0.02 margin means that the margin of the object is 2% of the smaller dimension of the screen)
    """

    @abstractmethod
    def __init__(self, game, size=(0, 0), visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, frame_hover_colour=None):
        super().__init__()

        # The game is passed as an attribute to access its attributes and methods:
        self.game = game

        # The UI elements with a relationship with the current one (used for responsive rendering):
        self.relations = []

        # Whether the UI element is visible:
        self.visible = visible

        # The display surface:
        self.display = pygame.display.get_surface()

        # Converting padding and margin from a ratio of the screen size to raw pixels:
        self.margin = self.game.unit_to_pixel(margin)
        self.padding = self.game.unit_to_pixel(padding)

        # When the frame/border/background should be shown:
        self.frame_condition = frame_condition
        # The colour of the frame:
        self.frame_colour = frame_colour
        if frame_hover_colour is None:
            self.frame_hover_colour = frame_colour
        else:
            self.frame_hover_colour = frame_hover_colour

        # Converting frame thickness and corner radius from a ratio of the screen size to pixels:
        self.thickness = self.game.unit_to_pixel(frame_thickness)
        self.corner_radius = self.game.unit_to_pixel(corner_radius)

        # Tentative size and position (0, 0), corrected afterwards:
        self.rect = pygame.Rect((0, 0), (0, 0))
        self.rect.center = position

        # The UI elements that have a relationship with this one:
        # These fields can be used to position UI elements by describing its relationship to another,
        # rather than explicitly using a position:
        self.above = above
        self.below = below
        self.to_left_of = to_left_of
        self.to_right_of = to_right_of
        self.centre_between = centre_between

        self.set_size(size)

    def calculate_position(self, exclusion_relations=None):

        # Placing item according to relation:
        if self.above is not None:
            self.place_above(self.above)
            if self.above not in self.relations:
                self.relations.append(self.above)
                self.above.add_relation(self)
        elif self.below is not None:
            self.place_below(self.below)
            if self.below not in self.relations:
                self.relations.append(self.below)
                self.below.add_relation(self)
        elif self.to_left_of is not None:
            self.place_to_left_of(self.to_left_of)
            if self.to_left_of not in self.relations:
                self.relations.append(self.to_left_of)
                self.to_left_of.add_relation(self)
        elif self.to_right_of is not None:
            self.place_to_right_of(self.to_right_of)
            if self.to_right_of not in self.relations:
                self.relations.append(self.to_right_of)
                self.to_right_of.add_relation(self)
        elif self.centre_between is not None:
            self.rect.center = self.get_centre_between(self.centre_between)

        # Re-positioning UI elements related to this one:
        self.adjust_relations(exclusion_relations=exclusion_relations)

    def adjust_relations(self, exclusion_relations=None):
        if exclusion_relations is None:
            exclusion_relations = []
        else:
            exclusion_relations = list(exclusion_relations)

        for relation in self.relations:
            if relation not in exclusion_relations:
                exclusion_relations.append(relation)
                relation.calculate_position(exclusion_relations=exclusion_relations)


    def add_relation(self, view):
        self.relations.append(view)

    def get_rect(self):
        return self.rect

    def get_margin(self):
        return self.margin

    def get_padding(self):
        return self.padding

    def set_size(self, size):
        # Setting accurate size including padding, whilst protecting the position of the centre:
        center = self.rect.center
        self.rect.size = [dimension + 2 * self.padding for dimension in self.game.unit_to_pixel_point(size)]
        self.rect.center = center
        self.calculate_position(exclusion_relations=(self,))

    def set_visibility(self, value):
        self.visible = value

    def place_above(self, view):
        # Placing the current UI element above the stated UI element, taking into account margins:
        self.rect.midbottom = (view.get_rect().midtop[0],
                               view.get_rect().midtop[1] - view.get_margin() - self.margin)

    def place_below(self, view):
        # Placing the current UI element below the stated UI element, taking into account margins:
        self.rect.midtop = (view.get_rect().midbottom[0],
                            view.get_rect().midbottom[1] + view.get_margin() + self.margin)

    def place_to_left_of(self, view):
        # Placing the current UI element to the left of the stated UI element, taking into account margins:
        self.rect.midright = (view.get_rect().midleft[0] - view.get_margin() - self.margin,
                              view.get_rect().midleft[1])

    def place_to_right_of(self, view):
        # Placing the current UI element to the right of the stated UI element, taking into account margins:
        self.rect.midleft = [view.get_rect().midright[0] + view.get_margin() + self.margin,
                             view.get_rect().midright[1]]

    @staticmethod
    def get_centre_between(points):
        # Places the UI element to the centre of 2 pre-existing UI elements
        value = (points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2
        return value

    def draw_frame(self, colour):
        # Drawing the frame of the UI element:
        pygame.draw.rect(self.display, colour, self.rect, self.thickness,
                         self.corner_radius)

    def draw(self):
        if not self.visible: return

        if self.hovering():
            if self.frame_condition != self.NEVER:
                self.draw_frame(self.frame_hover_colour)
        elif self.frame_condition == self.ALWAYS:
            self.draw_frame(self.frame_colour)

    def hovering(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self):
        return self.hovering() and self.game.mouse_released()


class TextLine(View):

    def __init__(self, game, text_string="", font_size=0.08, visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None,
                 centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=None, text_hover_colour=None):
        # Converting font size from a ratio of the screen size to pixels:
        self.font_size = game.unit_to_pixel(font_size)
        self.font = game.get_font(self.font_size)
        self.text_string = str(text_string)
        self.text = self.font.render(self.text_string, True, text_colour)

        # The colour of the text:
        self.text_colour = text_colour
        if text_hover_colour is None:
            self.text_hover_colour = text_colour
        else:
            self.text_hover_colour = text_hover_colour

        super().__init__(game, size=game.pixel_to_unit_point(self.text.get_size()), visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

    def get_text(self):
        return self.text_string

    def set_text(self, text_string):
        self.text_string = str(text_string)
        self.text = self.font.render(self.text_string, True, self.text_colour)
        self.set_size(self.game.pixel_to_unit_point(self.text.get_size()))

    def draw_text(self, colour):
        text_centre = self.rect.center
        text_size = self.text.get_size()
        text_top_left = (text_centre[0] - 0.5 * text_size[0], text_centre[1] - 0.5 * text_size[1])
        self.display.blit(self.font.render(self.text_string, True, colour), text_top_left)

    def draw(self):
        if not self.visible: return
        super().draw()
        if self.hovering():
            self.draw_text(self.text_hover_colour)
        else:
            self.draw_text(self.text_colour)

    def set_text_color(self, text_colour):
        self.text = self.font(self.font_size).render(self.text_string, True, text_colour)

    def set_italic(self, value):
        self.font.set_italic(value)
        self.text = self.font.render(self.text_string, True, self.text_colour)
        self.set_size(self.game.pixel_to_unit_point(self.text.get_size()))

    def set_bold(self, value):
        self.font.set_bold(value)
        self.text = self.font.render(self.text_string, True, self.text_colour)
        self.set_size(self.game.pixel_to_unit_point(self.text.get_size()))

    def set_underline(self, value):
        self.font.set_underline(value)
        self.text = self.font.render(self.text_string, True, self.text_colour)
        self.set_size(self.game.pixel_to_unit_point(self.text.get_size()))


class Text(View):

    # The line_separation_ratio variable is a ratio of the font size:
    def __init__(self, game, text_string="", font_size=0.08, line_separation_ratio=0.25, text_alignment=View.LEFT,
                 visible=True, position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None,
                 centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=None, text_hover_colour=None):
        # Converting font size from a ratio of the screen size to pixels:
        self.font_size = game.unit_to_pixel(font_size)
        self.font = game.get_font(self.font_size)
        self.game = game

        # Whether text should align left, right or centre:
        self.text_alignment = text_alignment

        # Converting line separation from a ratio of the screen size to pixels:
        self.line_separation = game.unit_to_pixel(font_size * line_separation_ratio)

        # The colour of the text:
        self.text_colour = text_colour
        self.text_hover_colour = text_hover_colour

        super().__init__(game, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        # Setting the text:
        self.text_strings = None
        self.text_lines = None
        self.set_text(text_string)

    def set_italic(self, value):
        for text_line in self.text_lines:
            text_line.set_italic(value)
        self.set_size(self.game.pixel_to_unit_point(self.calculate_size()))

    def set_bold(self, value):
        for text_line in self.text_lines:
            text_line.set_bold(value)
        self.set_size(self.game.pixel_to_unit_point(self.calculate_size()))

    def set_underline(self, value):
        for text_line in self.text_lines:
            text_line.set_underline(value)
        self.set_size(self.game.pixel_to_unit_point(self.calculate_size()))

    def set_text_colour(self, colour):
        for text_line in self.text_lines:
            text_line.set_text_colour(colour)
        self.set_size(self.game.pixel_to_unit_point(self.calculate_size()))

    def set_text(self, text_string):
        # The individual text strings are separated by line breaks:
        self.text_strings = list(str(text_string).split("\n"))

        self.position_texts()

    def position_texts(self):
        self.text_lines = []

        for index, text_string in enumerate(self.text_strings):
            # Creating text line object:
            # Creating and placing in different loops so that we know the size of the textbox before placing the texts:
            text_line = TextLine(self.game, text_string,
                                 position=(0, 0),
                                 font_size=self.game.pixel_to_unit(self.font_size),
                                 padding=self.game.pixel_to_unit(self.line_separation),
                                 margin=0,
                                 frame_condition=View.NEVER,
                                 text_colour=self.text_colour,
                                 text_hover_colour=self.text_hover_colour)
            self.text_lines.append(text_line)

        # Re-calculating its size and position to prevent overlap:
        self.set_size(self.game.pixel_to_unit_point(self.calculate_size()))
        self.calculate_position(exclusion_relations=(self,))

        # Placing the text lines:
        for index, text_line in enumerate(self.text_lines):
            # Placing y-position:
            if index == 0:
                y = self.rect.top + self.padding
            else:
                y = self.text_lines[index - 1].get_rect().bottom

            # Placing x-position:
            if self.text_alignment == View.LEFT:
                text_line.get_rect().topleft = (self.rect.left + self.padding, y)
            elif self.text_alignment == View.RIGHT:
                text_line.get_rect().topright = (self.rect.right - self.padding, y)
            else:  # text_alignment == View.CENTRE
                text_line.get_rect().midtop = (self.rect.centerx, y)

    def get_text_lines(self):
        return self.text_lines

    def calculate_size(self):
        max_horizontal = 0
        total_vertical = 0
        for text_line in self.text_lines:
            size = text_line.get_rect().size
            text_horizontal = size[0]
            if text_horizontal > max_horizontal:
                max_horizontal = text_horizontal
            total_vertical += size[1]
        return max_horizontal, total_vertical

    def draw(self):
        if not self.visible: return
        super().draw()
        for text_line in self.text_lines:
            text_line.draw()


class Image(View):

    def __init__(self, game, icon, size=(0.1, 0.1), visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK,
                 frame_hover_colour=None):
        # Setting up the image icon:
        self.icon = None

        super().__init__(game, size=size, visible=visible,
                         position=position, above=above, below=below, to_right_of=to_right_of, to_left_of=to_left_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        # The maximum size of the icon - the size of the button without padding:
        self.max_icon_size = size
        self.set_icon(icon)

    def set_icon(self, icon):
        self.icon = icon
        self.update_icon_size()

    def update_icon_size(self):
        # Updating the icon size whilst maintaining its aspect ratio:
        current_icon_size_px = self.icon.get_size()
        max_icon_size_px = self.game.unit_to_pixel_point(self.max_icon_size)
        icon_width = current_icon_size_px[0]
        icon_height = current_icon_size_px[1]

        if icon_width > icon_height:
            scale_factor = max_icon_size_px[0] / icon_width
            icon_width = max_icon_size_px[0]
            icon_height *= scale_factor
        else:
            scale_factor = max_icon_size_px[1] / icon_height
            icon_height = max_icon_size_px[1]
            icon_width *= scale_factor

        # Setting the icon with the adjusted size:
        self.icon = pygame.transform.scale(self.icon, (icon_width, icon_height))

    def set_size(self, size):
        super().set_size(size)
        if self.icon is not None:
            self.max_icon_size = size
            self.update_icon_size()

    def draw(self):
        super().draw()
        icon_centre = self.rect.center
        icon_size = self.icon.get_size()
        icon_top_left = (icon_centre[0] - 0.5 * icon_size[0], icon_centre[1] - 0.5 * icon_size[1])
        self.display.blit(self.icon, icon_top_left)


# Simply creates an instance of the correct UI object and uses
# the correct default values for implementing the UI object as a button:
class Button(View):

    def __init__(self, game, text_string=None, font_size=0.08, icon=None, size=(0.1, 0.1), visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.HOVER, frame_thickness=0.005, corner_radius=0.01, frame_colour=BLACK,
                 text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE):
        super().__init__(game, size=size, position=position, above=above, below=below, to_right_of=to_right_of,
                         to_left_of=to_left_of, centre_between=centre_between, margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        if text_string is not None:
            # The button is a text button:
            self.target = TextLine(game, text_string, font_size=font_size, visible=visible,
                                   position=position, above=above, below=below, to_right_of=to_right_of,
                                   to_left_of=to_left_of, centre_between=centre_between,
                                   margin=margin, padding=padding,
                                   frame_condition=frame_condition, frame_thickness=frame_thickness,
                                   corner_radius=corner_radius,
                                   frame_colour=frame_colour, text_colour=text_colour,
                                   frame_hover_colour=frame_hover_colour,
                                   text_hover_colour=text_hover_colour)
        elif icon is not None:
            # The button is an image button:
            self.target = Image(game, icon, size=size, visible=visible,
                                position=position, above=above, below=below, to_right_of=to_right_of,
                                to_left_of=to_left_of,
                                centre_between=centre_between,
                                margin=margin, padding=padding,
                                frame_condition=frame_condition, frame_thickness=frame_thickness,
                                corner_radius=corner_radius,
                                frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        self.__class__ = self.target.__class__
        self.__dict__ = self.target.__dict__


class Slider(View):

    def __init__(self, game, bar_size=(0.2, 0.005), handle_radius=0.01, start_value=(0, 0),
                 slide_horizontal=True, slide_vertical=False, visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 bar_colour=SILVER, handle_colour=BLACK, handle_hover_colour=IRIS):
        # The slider can have values between 0-1 for each axis.
        # Ensuring that the slider is centered on a given axis if it cannot slide on that axis:
        start_value = list(start_value)
        if not slide_horizontal: start_value[0] = 0.5
        if not slide_vertical: start_value[1] = 0.5

        self.slide_horizontal = slide_horizontal
        self.slide_vertical = slide_vertical
        self.value = start_value

        # The slider bar - this cannot simply be the frame of the parent since that encompasses padding.
        # The inheritance isn't perfect as this class doesn't use the frame, but it works as required nonetheless.
        # Tentative location value (0,0), corrected afterwards:
        self.bar = pygame.Rect((0, 0), game.unit_to_pixel_point(bar_size))

        # self.surface = pygame.Surface(game.unit_to_pixel_point(bar_size))
        # self.surface.fill(bar_colour)

        super().__init__(game, size=bar_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding)

        # Converting the handle radius from a ratio of the screen size to pixels:
        self.handle_radius = self.game.unit_to_pixel(handle_radius)

        self.bar_colour = bar_colour
        self.handle_colour = handle_colour
        self.handle_hover_colour = handle_hover_colour

        # Correcting the position of the bar:
        self.bar.center = self.rect.center

        # Whether the handle of the slider is being held:
        self.handle_held = False

        # The slider handle:
        self.handle_rect = pygame.Rect((0, 0), (2 * self.handle_radius, 2 * self.handle_radius))
        self.handle_rect.center = self.value_to_handle_position()

    def value_to_handle_position(self):
        # Converts the value of the handle into the pixel position of the handle on-screen:

        return [int((self.value[0] * self.bar.width) + self.bar.left),
                (int(self.bar.bottom - self.value[1] * self.bar.height))]

    def handle_position_to_value(self):
        # Converts the pixel position of the handle on-screen to its value:
        return [(self.handle_rect.centerx - self.bar.left) / self.bar.width,
                (self.bar.bottom - self.handle_rect.centery) / self.bar.height]

    def draw_bar(self):
        pygame.draw.rect(self.display, self.bar_colour, self.bar,
                         border_radius=self.corner_radius)

    def draw_handle(self, colour):
        if self.handle_grabbed():
            self.handle_held = True
        elif self.handle_released():
            self.handle_held = False

        if self.handle_held:
            # If the pointer is outside the slider, the handle of the slider should still be bound by the bar:
            if self.slide_horizontal:
                self.handle_rect.centerx = pygame.mouse.get_pos()[0]

                if self.handle_rect.centerx < self.bar.left:
                    self.handle_rect.centerx = self.bar.left
                elif self.handle_rect.centerx > self.bar.right:
                    self.handle_rect.centerx = self.bar.right
            else:
                self.handle_rect.centerx = self.bar.centerx

            if self.slide_vertical:
                self.handle_rect.centery = pygame.mouse.get_pos()[1]

                if self.handle_rect.centery < self.bar.top:
                    self.handle_rect.centery = self.bar.top
                elif self.handle_rect.centery > self.bar.bottom:
                    self.handle_rect.centery = self.bar.bottom
            else:
                self.handle_rect.centery = self.bar.centery

            # Updating the value of the handle:
            self.value = self.handle_position_to_value()

        # Drawing the handle:
        pygame.draw.circle(self.display, colour,
                           self.handle_rect.center,
                           self.handle_radius)

    def draw(self):
        if not self.visible: return
        self.draw_bar()
        # Drawing with the correct colour:
        if self.hovering():
            self.draw_handle(self.handle_hover_colour)
        else:
            self.draw_handle(self.handle_colour)

    def hovering(self):
        mouse_pos = pygame.mouse.get_pos()

        # Using the handle's radius to see if the mouse cursor is colliding with the handle:
        if ((self.handle_rect.centerx - mouse_pos[0]) ** 2 + (
                self.handle_rect.centery - mouse_pos[1]) ** 2) ** 0.5 <= self.handle_radius:
            return True
        return False

    def handle_grabbed(self):
        # Whether the handle has just been grabbed:
        return self.hovering() and self.game.mouse_pressed()

    def handle_released(self):
        # Whether the handle has just been grabbed:
        return self.handle_held and self.game.mouse_released()

    def get_value(self, decimal_places=None):
        if decimal_places is None:
            return self.value
        else:
            return [round(item, decimal_places) for item in self.value]

    def handle_is_held(self):
        return self.handle_held


class ProgressBar(View):

    def __init__(self, game, font_size=0.03, bar_size=(0.25, 0.025), start_progress=0,
                 orientation=View.HORIZONTAL, visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None, centre_between=None,
                 margin=0.02, padding=0.01,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 bar_colour=RED, frame_colour=BLACK, text_colour=WHITE,
                 frame_hover_colour=None, text_hover_colour=None):

        self.orientation = orientation

        # The slider bar - this cannot simply be the frame of the parent since that encompasses padding.
        # The inheritance isn't perfect as this class doesn't use the frame, but it works as required nonetheless.
        # Tentative location value (0,0), corrected afterwards:
        self.max_size = game.unit_to_pixel_point(bar_size)
        self.bar = pygame.Rect((0, 0), self.max_size)
        self.bar_colour = bar_colour

        super().__init__(game, size=bar_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour,)

        self.progress_text = TextLine(self.game,
                                      position=self.rect.center,
                                      font_size=font_size,
                                      frame_condition=View.NEVER,
                                      text_colour=text_colour, text_hover_colour=text_hover_colour)
        self.progress_text.get_rect().center = self.rect.center

        self.progress = None
        self.set_progress(start_progress)

    def set_progress(self, progress):
        self.progress = progress
        bar_size = self.progress_to_size()

        if self.orientation == View.HORIZONTAL:
            self.bar.width = bar_size
        else:
            self.bar.height = bar_size

        self.progress_text.set_text(Utils.percentage_format(self.progress))

    def progress_to_size(self):
        # Returns the position that the progress bar should end given the current progress:
        if self.orientation == View.HORIZONTAL:
            dimension = self.max_size[0]
        else:
            dimension = self.rect.height

        return int((self.progress * dimension))


    def draw_progress(self):
        pygame.draw.rect(self.display, self.bar_colour, self.bar, border_radius=self.corner_radius)

    def draw(self):
        # Aligning rectangles:
        self.bar.topleft = self.rect.topleft + pygame.Vector2(self.padding, self.padding)
        self.progress_text.get_rect().center = self.bar.center
        super().draw()
        self.draw_progress()
        self.progress_text.draw()


# A UI element that cycles through strings when clicked:
class Selector(TextLine):

    def __init__(self, game, selection_strings=(OFF, ON), start_index=0, font_size=0.08, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.HOVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE):
        # Whether the slider has just been incremented:
        self.incremented = False

        # The strings the selector will cycle through:
        self.selection_strings = [str(string) for string in selection_strings]
        self.selection_index = start_index

        super().__init__(game, self.selection_strings[self.selection_index], font_size=font_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, text_colour=text_colour, frame_hover_colour=frame_hover_colour,
                         text_hover_colour=text_hover_colour)

    def draw(self):
        if not self.visible: return
        # Drawing is essentially identical to parent:
        self.set_text(self.get_state())
        super().draw()

    def increment(self):
        self.selection_index += 1
        if self.selection_index >= len(self.selection_strings):
            self.selection_index = 0

        self.incremented = True

    def get_state(self):
        # It is necessary to update the state here.
        # if we didi not, when we call this function after the selector is clicked,
        # we would get the state just before the click.

        # We cannot update the state in the draw function because that is called at the end of the game loop.

        if self.clicked():
            if not self.incremented:
                # If the slider has just been clicked and not yet incremented, increment it:
                self.increment()

        else:
            self.incremented = False

        return self.selection_strings[self.selection_index]


class TextInput(TextLine):
    # Input Type:
    STRING = 0
    INTEGER = 1
    FLOAT = 2

    def __init__(self, game, text_string="", font_size=0.08, max_length=50, hint=PLACEHOLDER, clear_on_focus=False,
                 input_type=STRING, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, centre_between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE,
                 frame_focus_colour=IRIS, text_focus_colour=IRIS):
        # The input type that is allowed:
        self.input_type = input_type

        # The text is displayed if the element is empty:
        self.hint = hint

        # The maximum length of text input:
        self.max_length = max_length

        # Whether to set input as hint and clear input field when unfocused.
        # Means that there is no need to delete previous input when entering new input.
        self.clear_on_focus = clear_on_focus

        # Whether the element is currently in focus:
        self.in_focus = False

        # The colours for when the element is in focus - it has been clicked and currently editing:
        self.focus_frame_colour = frame_focus_colour
        self.focus_text_colour = text_focus_colour

        # If there is no text already present, showing the hint:
        if text_string is None:
            text_string = hint
            # Whether the hint is currently being shown:
            self.hint_active = True
        else:
            self.hint_active = False

        super().__init__(game, text_string, font_size=font_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         centre_between=centre_between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, text_colour=text_colour, frame_hover_colour=frame_hover_colour,
                         text_hover_colour=text_hover_colour)

    def draw(self):
        if not self.visible: return

        # If option enabled and the element has just been unfocused,
        # setting text as hint and clearing the text field:
        if self.clear_on_focus and self.unfocused() and self.text_string != "":
            self.set_hint(self.text_string)
            self.set_text("")

        if self.clicked():
            self.in_focus = True
        elif self.unfocused():
            self.in_focus = False

        if self.in_focus:
            self.draw_frame(self.focus_frame_colour)
            self.draw_text(self.focus_text_colour)

            # Removing the hint so that text can be input:
            if self.hint_active:
                self.set_text("")
                self.hint_active = False

            self.handle_input()
        else:
            # If the input length is 0 and the text is not in focus, showing hint:
            if len(self.text_string) == 0 and not self.in_focus:
                self.hint_active = True
                self.set_text(self.hint)

            # When not in focus, drawn just like parent:
            super().draw()

    def handle_input(self):
        keys = self.game.get_key_down_events()

        if len(keys) > 0:
            # Iterating through each key press because if multiple keys are
            # pressed in a single frame, all need to be registered:
            for key in keys:
                if key == pygame.K_BACKSPACE:
                    # Deleting if backspace is pressed:
                    self.set_text(self.text_string[:-1])

                elif (len(self.text_string) < self.max_length) and self.input_type_allowed(key):
                    # If the input field has not reached the maximum allowed length,
                    # and the key pressed is allowed, adding it to the text input:

                    # Auto-cap after spaces:
                    if self.input_empty() or (len(self.text_string) > 0 and self.text_string[-1] == " "):
                        self.set_text(self.text_string + chr(key).upper())
                    else:
                        self.set_text(self.text_string + chr(key).lower())

    def unfocused(self):
        # Whether the UI element has just lost focus:
        return ((not self.hovering()) and self.game.mouse_released()) \
               or pygame.K_RETURN in self.game.get_key_down_events()

    def input_type_allowed(self, key):
        # Wrapping in try-catch since some keys do not have a string value:
        try:
            key_string = chr(key)

            # Any key corresponding to a string is allowed:
            if self.input_type == self.STRING:
                return True
            elif self.input_type == self.INTEGER:
                # Any number is allowed.
                # We can know we have an integer because the floating point is not allowed:
                return key_string.isnumeric()
                # There won't be any need to input negative numbers, so not allowing that.
            elif self.input_type == self.FLOAT:
                # Any number or the floating point is allowed.
                return key_string == "." or key_string.isnumeric()

        except ValueError:
            # If key does not have a string value, not allowing:
            return False

    def input_empty(self):
        return self.text_string == "" or self.text_string == self.hint

    def get_hint(self):
        return self.hint

    def set_hint(self, hint):
        self.hint = hint
