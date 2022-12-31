from colours import *
from abc import ABC, abstractmethod
from utils import *
import pygame


"""
This is my own UI framework, providing a dynamic component library, layout management, and responsive rendering.
"""

"""
IMPORTANT: For attributes such as margin, padding, frame_thickness, corner_radius, font_size, etc.
Their values are the proportion of the screen which they should occupy, since the game needs to be
resolution independent, and passing those values as pixels would prevent this.
(i.e. 0.02 margin means that the margin of the object is 2% of the smaller dimension of the screen)
"""


# An abstract class which all the UI elements inherit from: [TESTED & FINALISED]
class View(ABC, pygame.sprite.Sprite):
    # When the frame (border / background) of the UI element should be shown:
    NEVER = 0
    ALWAYS = 1
    HOVER = 2
    # FOCUS = 3

    # Text Alignment:
    # (Storing here so that it is accessible as a default value from Text constructor)
    CENTRE = 0
    LEFT = 1
    RIGHT = 2

    # Orientation
    HORIZONTAL = 0
    VERTICAL = 1

    @abstractmethod
    def __init__(self, game, size=(0, 0), visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, frame_hover_colour=None):
        super().__init__()

        # The game is passed as an argument to access some of its attributes and methods:
        self.game = game

        # A list of all UI elements that are directly related to this one (used for responsive rendering).
        # This list does not include elements that are related indirectly.
        self.relatives = []

        # Whether the UI element is visible (i.e. if it should be drawn):
        self.visible = visible

        # The display surface:
        self.display = pygame.display.get_surface()

        # Converting the following from a ratio of the screen size to raw pixels:
        self.margin = self.game.unit_to_pixel(margin)
        self.padding = self.game.unit_to_pixel(padding)
        self.frame_thickness = self.game.unit_to_pixel(frame_thickness)
        self.corner_radius = self.game.unit_to_pixel(corner_radius)

        # When the frame/border/background should be shown:
        self.frame_condition = frame_condition
        # The colour of the frame:
        self.frame_colour = frame_colour
        # If not specified, hover colours will be the same as the default colours:
        if frame_hover_colour is None: self.frame_hover_colour = frame_colour
        else: self.frame_hover_colour = frame_hover_colour

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
        self.between = between

        self.set_size(size)

    def set_size(self, size):
        # Setting accurate size including padding, whilst protecting the position of the centre:
        centre = self.rect.center
        self.rect.size = [dimension + 2 * self.padding for dimension in self.game.unit_to_pixel_point(size)]
        self.rect.center = centre
        # Because the size of the object has changed, the related objects may need to shift to provide space,
        # so triggering this behaviour:
        self.calculate_position()

    def calculate_position(self, exclude=None):
        # All UI elements keep a list of the UI elements that they are related to,
        # so that when one of them moves or changes in size, all the other ones can adjust their positions.
        relations = [self.above, self.below, self.to_left_of, self.to_right_of, self.between]
        placement_methods = [self.place_above, self.place_below, self.place_to_left_of, self.place_to_right_of,
                             self.place_between]

        # Iterating over each relative attribute and if it is not None,
        # calling the appropriate method to position item in relation to the relative:
        for index, relative in enumerate(relations):
            if relative is not None:
                placement_methods[index](relative)
                if relative not in self.relatives and isinstance(relative, View):
                    # If relative not already in the relatives list, adding it,
                    # and adding this object to the relative's list:
                    self.add_relative(relative)
                    relative.add_relative(self)

        # Adding UI elements we have just repositioned into an exclusion list to prevent infinite recursion:
        if exclude is None: exclude = []
        else: exclude = list(exclude)

        # The current UI element has just been re-positioned, so adding it to the exclusion list:
        exclude.append(self)

        # Re-positioning other UI elements whose positions depend on this one:
        for relative in self.relatives:
            if relative not in exclude:
                # Triggering the repositioning of each UI element not already re-positioned.
                # These will in turn trigger the re-positioning of the element related to them,
                # and so on, adjusting the whole UI layout as necessary:
                relative.calculate_position(exclude=exclude)

    def add_relative(self, view):
        self.relatives.append(view)

    def get_rect(self):
        return self.rect

    def get_margin(self):
        return self.margin

    def get_padding(self):
        return self.padding

    def get_visibility(self):
        return self.visible

    def set_visibility(self, visibility):
        self.visible = visibility

    def place_above(self, above):
        if isinstance(above, View):
            # Placing the current UI element above the stated UI element, taking into account margins:
            self.rect.midbottom = (above.get_rect().midtop[0],
                                   above.get_rect().midtop[1] - above.get_margin() - self.margin)

        elif isinstance(above, tuple) or isinstance(above, list):
            # Placing the current UI element above the stated point, taking into account margins:
            self.rect.midbottom = (above[0], above[1] - self.margin)

    def place_below(self, below):
        if isinstance(below, View):
            # Placing the current UI element below the stated UI element, taking into account margins:
            self.rect.midtop = (below.get_rect().midbottom[0],
                                below.get_rect().midbottom[1] + below.get_margin() + self.margin)
        elif isinstance(below, tuple) or isinstance(below, list):
            # Placing the current UI element below the stated point, taking into account margins:
            self.rect.midtop = (below[0], below[1] + self.margin)

    def place_to_left_of(self, to_left_of):
        if isinstance(to_left_of, View):
            # Placing the current UI element below the stated UI element, taking into account margins:
            self.rect.midright = (to_left_of.get_rect().midleft[0] - to_left_of.get_margin() - self.margin,
                                  to_left_of.get_rect().midleft[1])
        elif isinstance(to_left_of, tuple) or isinstance(to_left_of, list):
            # Placing the current UI element below the stated point, taking into account margins:
            self.rect.midright = (to_left_of[0] - self.margin, to_left_of[1])

    def place_to_right_of(self, to_right_of):
        if isinstance(to_right_of, View):
            # Placing the current UI element to the right of the stated UI element, taking into account margins:
            self.rect.midleft = (to_right_of.get_rect().midright[0] + to_right_of.get_margin() + self.margin,
                                 to_right_of.get_rect().midright[1])
        elif isinstance(to_right_of, tuple) or isinstance(to_right_of, list):
            # Placing the current UI element to the right of the stated point, taking into account margins:
            self.rect.midbottom = (to_right_of[0] + self.margin, to_right_of[1] - self.margin)

    @staticmethod
    def get_midpoint(point_1, point_2):
        # Returns the midpoint between two points:
        return (point_1[0] + point_2[0]) / 2, (point_1[1] + point_2[1]) / 2

    def place_between(self, relations):
        points = []

        for relation in relations:
            # Checking if each relation is a UI element or a point:
            if isinstance(relation, View):
                if relation not in self.relatives:
                    # Adding relative here, as it is not possible to do so in
                    # calculate_position() since the between attribute is a tuple:
                    self.add_relative(relation)
                    relation.add_relative(self)
                points.append(relation.get_rect().center)
            else:
                points.append(relation)
        self.rect.center = self.get_midpoint(points[0], points[1])

    def get_frame_condition(self):
        return self.frame_condition

    def set_frame_condition(self, condition):
        self.frame_condition = condition

    def get_frame_colour(self):
        return self.frame_colour

    def set_frame_colour(self, colour):
        self.frame_colour = colour

    def get_frame_hover_colour(self):
        return self.frame_hover_colour

    def set_frame_hover_colour(self, colour):
        self.frame_hover_colour = colour

    def get_corner_radius(self):
        return self.corner_radius

    def set_corner_radius(self, corner_radius):
        self.corner_radius = self.game.unit_to_pixel(corner_radius)

    def get_thickness(self):
        return self.frame_thickness

    def set_thickness(self, thickness):
        self.frame_thickness = self.game.unit_to_pixel(thickness)

    def hovering(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self):
        return self.hovering() and self.game.mouse_released()

    def draw_frame(self, colour):
        # Drawing the frame of the UI element with the specified colour:
        pygame.draw.rect(self.display, colour, self.rect, self.frame_thickness, self.corner_radius)

    def draw(self):
        # Determining how to draw the frame of the element:
        if self.hovering() and self.frame_condition != self.NEVER:
            self.draw_frame(self.frame_hover_colour)
        elif self.frame_condition == self.ALWAYS:
            self.draw_frame(self.frame_colour)

    def update(self):
        if self.visible: self.draw()


# A single line of text: [TESTED & FINALISED]
class TextLine(View):

    def __init__(self, game, text="", font_size=0.08, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.02, bold=False, italic=False, underline=False,
                 frame_condition=View.NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=None, text_hover_colour=None):
        # Converting font size from a ratio of the screen size to pixels:
        self.font_size = game.unit_to_pixel(font_size)
        self.font = game.get_font(self.font_size)

        # Setting the text style:
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        self.font.set_underline(underline)

        self.text = str(text)
        self.text_surface = self.font.render(self.text, True, text_colour)
        # This will be set when the position is calculated:
        self.text_rect = None

        self.text_colour = text_colour

        # If not specified, hover colours will be the same as the default colours:
        if text_hover_colour is None: self.text_hover_colour = text_colour
        else: self.text_hover_colour = text_hover_colour

        super().__init__(game, size=game.pixel_to_unit_point(self.text_surface.get_size()), visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         between=between, margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)


    def calculate_position(self, exclude=None):
        super().calculate_position(exclude=exclude)
        # Centering the text surface after the frame has been moved:
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.rect.center

    def get_text(self):
        return self.text

    def set_text(self, text_string):
        self.text = str(text_string)
        # Need to update the text surface to be able to calculate the new size:
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        # The size of the whole UI element has changed so updating it:
        self.set_size(self.game.pixel_to_unit_point(self.text_surface.get_size()))

    def get_font_size(self):
        return self.font_size

    def set_font_size(self, font_size):
        self.font_size = self.game.unit_to_pixel(font_size)

        # Need to maintain text style:
        bold = self.font.get_bold()
        italic = self.font.get_italic()
        underline = self.font.get_underline()

        # Updating the font size:
        self.font = self.game.get_font(self.font_size)

        # Correcting text style:
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        self.font.set_underline(underline)

        # Need to update the text surface to be able to calculate the new size:
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        # The size of the whole UI element has changed so updating it:
        self.set_size(self.game.pixel_to_unit_point(self.text_surface.get_size()))

    def get_text_colour(self):
        return self.text_colour

    def set_text_colour(self, text_colour):
        self.text_colour = text_colour

    def get_text_hover_colour(self):
        return self.text_hover_colour

    def set_text_hover_colour(self, text_hover_colour):
        self.text_hover_colour = text_hover_colour

    def get_bold(self):
        return self.font.get_bold()

    def set_bold(self, value):
        # Using font object to keep track of text style:
        self.font.set_bold(value)
        # Need to update the text surface to be able to calculate the new size:
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        # Setting size again since it has changed:
        self.set_size(self.game.pixel_to_unit_point(self.text_surface.get_size()))

    def get_italic(self):
        return self.font.get_italic()

    def set_italic(self, value):
        # Using font object to keep track of text style:
        self.font.set_italic(value)
        # Need to update the text surface to be able to calculate the new size:
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        # Setting size again since it has changed:
        self.set_size(self.game.pixel_to_unit_point(self.text_surface.get_size()))

    def get_underline(self):
        return self.font.get_underline()

    def set_underline(self, value):
        # Using font object to keep track of text style:
        self.font.set_underline(value)
        # Need to update the text surface to be able to calculate the new size:
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        # Setting size again since it has changed:
        self.set_size(self.game.pixel_to_unit_point(self.text_surface.get_size()))

    def draw_text(self, colour):
        # Rendering again to obtain the correct colour:
        self.text_surface = self.font.render(self.text, True, colour)
        self.display.blit(self.text_surface, self.text_rect)

    def draw(self):
        super().draw()
        if self.hovering():
            self.draw_text(self.text_hover_colour)
        else:
            self.draw_text(self.text_colour)


# An image with a frame: [TESTED & FINALISED]
class Image(View):

    def __init__(self, game, icon, size=(0.1, 0.1), visible=True,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None, between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.NEVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, frame_hover_colour=None):
        self.icon = None
        self.icon_rect = pygame.Rect((0, 0), (0, 0))

        super().__init__(game, size=size, visible=visible,
                         position=position, above=above, below=below, to_right_of=to_right_of, to_left_of=to_left_of,
                         between=between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        # The maximum size of the icon - the size of the button without padding:
        self.max_icon_size = size
        self.set_icon(icon)

    def calculate_position(self, exclude=None):
        super().calculate_position(exclude=exclude)
        # Centering the icon surface after the frame has been moved:
        self.icon_rect.center = self.rect.center

    def set_icon(self, icon):
        self.icon = icon
        self.update_icon_size()

    def update_icon_size(self):
        # Updating the icon size whilst maintaining its aspect ratio and obeying the maximum size:
        current_icon_size_px = self.icon.get_size()
        max_icon_size_px = self.game.unit_to_pixel_point(self.max_icon_size)
        icon_width = current_icon_size_px[0]
        icon_height = current_icon_size_px[1]

        if (icon_width / max_icon_size_px[0]) > (icon_height / max_icon_size_px[1]):
            # If width greater than height, adjusting width to fit max width,
            # then multiplying height with the scale factor:
            scale_factor = max_icon_size_px[0] / icon_width
            icon_width = max_icon_size_px[0]
            icon_height *= scale_factor
        else:
            # If width greater than height, adjusting width to fit max width,
            # then multiplying height with the scale factor:
            scale_factor = max_icon_size_px[1] / icon_height
            icon_height = max_icon_size_px[1]
            icon_width *= scale_factor

        # Setting the adjusted size::
        self.icon = pygame.transform.scale(self.icon, (icon_width, icon_height))
        # Only changing the size of the icon to not lose position value:
        self.icon_rect.size = self.icon.get_rect().size
        # Changing size maintains the position of the top left corner by default, so centering the icon:
        self.icon_rect.center = self.rect.center

    def set_size(self, size):
        super().set_size(size)
        if self.icon is not None:
            # Updating the icon size to fit the new maximum size:
            self.max_icon_size = size
            self.update_icon_size()

    def draw_icon(self):
        self.display.blit(self.icon, self.icon_rect)

    def draw(self):
        super().draw()
        self.draw_icon()


# A button that is actually a line of text or image: [TESTED & FINALISED]
class Button(View):

    def __init__(self, game, text=None, font_size=0.08, icon=None, size=(0.1, 0.1),
                 visible=True, position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None,
                 between=None, margin=0.02, padding=0.02, bold=False, italic=False, underline=False,
                 frame_condition=View.HOVER, frame_thickness=0.005, corner_radius=0.01, frame_colour=BLACK,
                 text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE):
        super().__init__(game, size=size, position=position, above=above, below=below, to_right_of=to_right_of,
                         to_left_of=to_left_of, between=between, margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        if text is not None:
            # The button is a text button:
            self.target = TextLine(game, text, font_size=font_size, visible=visible,
                                   position=position, above=above, below=below, to_right_of=to_right_of,
                                   to_left_of=to_left_of, between=between,
                                   margin=margin, padding=padding, bold=bold, italic=italic, underline=underline,
                                   frame_condition=frame_condition, frame_thickness=frame_thickness,
                                   corner_radius=corner_radius,
                                   frame_colour=frame_colour, text_colour=text_colour,
                                   frame_hover_colour=frame_hover_colour, text_hover_colour=text_hover_colour)
        elif icon is not None:
            # The button is an image button:
            self.target = Image(game, icon, size=size, visible=visible,
                                position=position, above=above, below=below, to_left_of=to_left_of,
                                to_right_of=to_right_of, between=between,
                                margin=margin, padding=padding,
                                frame_condition=frame_condition, frame_thickness=frame_thickness,
                                corner_radius=corner_radius,
                                frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        # Transferring attributes and methods from target.
        self.__class__ = self.target.__class__
        self.__dict__ = self.target.__dict__


# A UI element that cycles through text strings when clicked: [TESTED & FINALISED]
class Selector(TextLine):

    def __init__(self, game, texts=(OFF, ON), start_index=0, font_size=0.08, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.HOVER, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE):
        # The texts the selector will cycle through:
        self.selection_texts = [str(text) for text in texts]
        # If not in range, setting to 0:
        if not 0 <= start_index < len(texts):
            start_index = 0
        self.selection_index = start_index

        # Whether the text shown has just been incremented:
        self.incremented = False

        super().__init__(game, self.selection_texts[self.selection_index], font_size=font_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         between=between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, text_colour=text_colour, frame_hover_colour=frame_hover_colour,
                         text_hover_colour=text_hover_colour)

    def increment(self):
        # Whether the selector has been incremented this frame:
        self.incremented = True

        self.selection_index += 1
        # If not in range, setting to 0:
        if self.selection_index >= len(self.selection_texts):
            self.selection_index = 0

        # Setting the new text:
        self.set_text(self.selection_texts[self.selection_index])

    def update_state(self):
        # If clicked and not yet incremented, selection should be incremented.
        # If not clicked, the incremented flag should be reset:
        if self.clicked():
            if not self.incremented:
                self.increment()
        else:
            self.incremented = False

    def get_state(self):
        # If the item is clicked in the same frame that the state is obtained,
        # current state will not have been incremented yet, and thus be incorrect.
        # So updating the state before returning it:
        self.update_state()
        return self.selection_texts[self.selection_index]

    def update(self):
        self.update_state()
        super().update()


# A UI element that accepts a single-line keyboard input: [TESTED & FINALISED]
class TextInput(TextLine):
    # Input Types:
    STRING = 0
    UNSIGNED_INTEGER = 1
    SIGNED_INTEGER = 2
    UNSIGNED_REAL = 3
    SIGNED_REAL = 4

    def __init__(self, game, text="", font_size=0.08, max_length=50, hint=PLACEHOLDER, clear_on_submit=False,
                 input_type=STRING, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=SMOKE, text_hover_colour=SMOKE,
                 frame_focus_colour=BLUE_GREY, text_focus_colour=BLUE_GREY):
        # The input type that is allowed:
        self.input_type = input_type

        # The hint is displayed if the element is empty:
        self.hint = hint

        # Whether the hint is currently being shown:
        self.hint_active = text in [None, ""]

        # If there is no text already present, showing the hint:
        if self.hint_active: text = hint

        # The maximum length of text input:
        self.max_length = max_length

        # Whether to set input as hint and clear input field when text is submitted.
        # This prevents the need to delete what has already been written should the user want to change it.
        self.clear_on_submit = clear_on_submit

        # Whether the element is currently in focus -  if it has been clicked and is currently being edited:
        self.in_focus = False

        # The colours for when the element is in focus:
        self.focus_frame_colour = frame_focus_colour
        self.focus_text_colour = text_focus_colour

        super().__init__(game, text, font_size=font_size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         between=between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, text_colour=text_colour, frame_hover_colour=frame_hover_colour,
                         text_hover_colour=text_hover_colour)

    def handle_input(self):
        keys = self.game.get_key_down_events()

        # Iterating through each key press because if multiple keys are
        # pressed in a single frame, all need to be registered:
        for key in keys:
            # Deleting last character if backspace is pressed:
            if key == pygame.K_BACKSPACE:
                self.set_text(self.text[:-1])

            # If the input field is less than the maximum allowed,
            # and the key pressed is valid, adding it to the text input:
            elif (len(self.text) < self.max_length) and self.input_key_allowed(key):
                if len(self.text) == 0 or self.text[-1] == " ":
                    # Auto-cap after spaces and for the first character:
                    self.set_text(self.text + chr(key).upper())
                else:
                    # Other characters lower case:
                    self.set_text(self.text + chr(key).lower())

    def input_key_allowed(self, key):
        # Wrapping in try-catch since some keys do not have a string value:
        try:
            key_string = chr(key)

            if self.input_type == self.STRING:
                return True
            elif self.input_type == self.UNSIGNED_INTEGER:
                # Only numbers are allowed - no decimal point or signs:
                return key_string.isnumeric()
            elif self.input_type == self.SIGNED_INTEGER:
                # Only numbers and the minus sign are allowed - no decimal point:
                return key_string.isnumeric() or key_string == "-"
            elif self.input_type == self.UNSIGNED_REAL:
                # Only numbers and the decimal point are allowed - no signs:
                return key_string.isnumeric() or key_string == "."
            elif self.input_type == self.SIGNED_REAL:
                # Any number, the decimal point  and the negative signs are allowed.
                return key_string in [".", "-"] or key_string.isnumeric()

        except ValueError:
            # If the key does not have a string value, it is invalid:
            return False

    def input_empty(self):
        # The input is empty if the hint is active or the text is empty:
        return self.text == "" or self.hint_active

    def get_hint(self):
        return self.hint

    def set_hint(self, hint):
        self.hint = hint

    def submitted(self):
        # Whether the text has just been submitted:
        return ((not self.hovering()) and self.game.mouse_released()) \
               or pygame.K_RETURN in self.game.get_key_down_events()

    def draw(self):
        if self.in_focus:
            # If in focus, drawing with focus colours:
            self.draw_frame(self.focus_frame_colour)
            self.draw_text(self.focus_text_colour)
        else:
            # If the element is not in focus, drawing is same as parent:
            super().draw()

    def update(self):
        # Setting the item to be in focus from when it is clicked
        # until the user clicks elsewhere or presses ENTER:
        if self.clicked(): self.in_focus = True
        elif self.submitted():
            # Once submitted, the element is no longer in focus:
            self.in_focus = False

            # If the option is enabled, setting the input as the hint and clearing the text field:
            if self.clear_on_submit and len(self.text) > 0:
                self.set_hint(self.text)
                self.set_text("")

        if self.in_focus:
            # If the hint is active, clearing it when the user clicks on the text box:
            if self.hint_active:
                self.set_text("")
                self.hint_active = False

            # If the item is in focus, the user may be typing:
            self.handle_input()
        else:
            # If the input length is 0 and the text is not in focus, showing hint:
            if len(self.text) == 0:
                self.hint_active = True
                self.set_text(self.hint)

        super().update()


# A paragraph of text: [TESTED & FINALISED]
class Text(View):

    # The line_separation_ratio is a ratio of the font size:
    def __init__(self, game, text="", font_size=0.08, visible=True,
                 line_separation_ratio=0.5, text_alignment=View.LEFT,
                 position=(0, 0), above=None, below=None, to_right_of=None, to_left_of=None,
                 between=None,
                 margin=0.02, padding=0.02, bold=False, italic=False, underline=False,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 frame_colour=BLACK, text_colour=BLACK, frame_hover_colour=None, text_hover_colour=None):
        # This class must inherit from View instead of from TextLine
        # since the object itself contains multiple text lines, but itself is not a TextLine.
        # Therefore, need to have these attributes here:
        self.font_size = game.unit_to_pixel(font_size)
        self.font = game.get_font(self.font_size)

        # Setting the text style:
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        self.font.set_underline(underline)

        # The colour of the text:
        self.text_colour = text_colour
        # If not specified, hover colours will be the same as the default colours:
        if text_hover_colour is None: self.text_hover_colour = text_colour
        else: self.text_hover_colour = text_hover_colour

        # Whether text should align left, right or centre:
        self.text_alignment = text_alignment

        # line_separation_ratio is a ratio of how much space there should be between lines:
        # i.e. a ratio of 2 would mean that the space between each line is twice the font size:
        # Converting line separation from a ratio of the text size to pixels:
        self.line_separation_ratio = line_separation_ratio
        self.line_separation = game.unit_to_pixel(font_size * line_separation_ratio)

        # A list of text strings for each line of the paragraph:
        self.text_strings = None
        # A list of TextLine objects which make up the paragraph:
        self.text_lines = None

        super().__init__(game, visible=visible, position=position, above=above, below=below, to_left_of=to_left_of,
                         to_right_of=to_right_of,
                         between=between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        # Setting the text:
        self.set_text(text)

    def get_bold(self):
        return self.font.get_bold()

    def set_bold(self, value):
        # Using font object to keep track of text style:
        self.font.set_bold(value)
        for text_line in self.text_lines: text_line.set_bold(value)
        # Setting size again since it has changed:
        self.set_size(self.calculate_size())

    def get_italic(self):
        return self.font.get_italic()

    def set_italic(self, value):
        # Using font object to keep track of text style:
        self.font.set_italic(value)
        for text_line in self.text_lines: text_line.set_italic(value)
        # Setting size again since it has changed:
        self.set_size(self.calculate_size())

    def get_underline(self):
        return self.font.get_underline()

    def set_underline(self, value):
        # Using font object to keep track of text style:
        self.font.set_underline(value)
        for text_line in self.text_lines: text_line.set_underline(value)
        # Setting size again since it has changed:
        self.set_size(self.calculate_size())

    def set_text_colour(self, colour):
        for text_line in self.text_lines:
            text_line.set_text_colour(colour)

    def get_text(self):
        return self.text_strings

    def get_text_lines(self):
        return self.text_lines

    def get_font_size(self):
        return self.font_size

    def set_font_size(self, font_size):
        # Setting the font size for each line of text:
        for text_line in self.text_lines: text_line.set_font_size(font_size)

        # Calculating the new line separation:
        self.line_separation = self.game.unit_to_pixel(font_size * self.line_separation_ratio)

        # No need to re-position texts here since it will be done when calculating size:
        self.set_size(self.calculate_size())

    def get_text_alignment(self):
        return self.text_alignment

    def set_alignment(self, text_alignment):
        self.text_alignment = text_alignment
        self.position_texts()

    def create_texts(self):
        self.text_lines = []

        # Text styles are the same for all the lines:
        bold = self.font.get_bold()
        italic = self.font.get_italic()
        underline = self.font.get_underline()

        for index, text_string in enumerate(self.text_strings):
            # Creating TextLine object:
            text_line = TextLine(self.game, text_string,
                                 position=(0, 0),
                                 # Font size must be in pixels:
                                 font_size=self.game.pixel_to_unit(self.font_size),
                                 # Implementing the line separation as the margin for each line:
                                 # Using half the line separation because there are 2 text lines,
                                 # each with margin on all sides:
                                 padding=0, margin=0.5 * self.game.pixel_to_unit(self.line_separation),
                                 # Setting text style:
                                 bold=bold, italic=italic, underline=underline,
                                 # Individual text lines should not have a frame:
                                 frame_condition=View.NEVER,
                                 text_colour=self.text_colour,
                                 text_hover_colour=self.text_hover_colour)
            self.text_lines.append(text_line)

    def set_text(self, text_string):
        # The individual text strings for each line are separated by line breaks:
        self.text_strings = list(str(text_string).split("\n"))

        # Determining if the text lines need to be created or if we can just use existing ones:
        # The expression before the AND gate may seem redundant,
        # but we need to ensure that text_lines is not None to get its length.
        if self.text_lines is None or (self.text_lines is not None and len(self.text_lines) != len(self.text_strings)):
            # Not ideal to create all TextLine objects again
            # - ideally should create/remove only as many as necessary:
            self.create_texts()
        elif self.text_lines is not None:
            # We can simply re-purpose the existing lines of text:
            for index, text_line in enumerate(self.text_lines): text_line.set_text(self.text_strings[index])

        # Positioning the text lines:
        self.position_texts()
        # Re-calculating its size and position to prevent overlap:
        self.set_size(self.calculate_size())

    def position_texts(self):
        # Placing the text lines:
        # We have to place them like this instead of using relative UI placement to allow for text alignment:
        for index, text_line in enumerate(self.text_lines):
            # Determining y-position:
            if index == 0:
                y = self.rect.top + self.padding + text_line.get_margin()
            else:
                previous_text_line = self.text_lines[index - 1]
                y = previous_text_line.get_rect().bottom + previous_text_line.get_margin() + text_line.get_margin()

            # Determining x_position and placing:
            if self.text_alignment == View.LEFT:
                text_line.get_rect().topleft = (self.rect.left + self.padding, y)
            elif self.text_alignment == View.RIGHT:
                text_line.get_rect().topright = (self.rect.right - self.padding, y)
            else:  # text_alignment == View.CENTRE
                text_line.get_rect().midtop = (self.rect.centerx, y)

            # Causing the text surfaces within each text line to be centred into the invisible frame:
            text_line.calculate_position()

    def calculate_size(self):
        max_horizontal = 0
        total_vertical = 0
        for text_line in self.text_lines:
            # Adding the margin of each text line into the size calculation:
            # Adding twice the margin since there is margin for top and bottom:
            # Not including horizontal margin since it represents text line separation:
            size = text_line.get_rect().size + pygame.Vector2(0, 2 * text_line.margin)

            # Determining if the maximum horizontal size has increased:
            max_horizontal = max(max_horizontal, size[0])
            # Increasing the total vertical size:
            total_vertical += size[1]

        return self.game.pixel_to_unit_point((max_horizontal, total_vertical))

    def calculate_position(self, exclude=None):
        super().calculate_position(exclude=exclude)
        # We cannot position the texts if they do not exist yet,
        # and the base element is just being created:
        if self.text_lines is not None:
            # Updating the position of the individual text surfaces:
            self.position_texts()

    def update(self):
        super().update()
        for text_line in self.text_lines:
            text_line.update()


# A slider that can slide horizontally, vertically or both: [TESTED & FINALISED]
class Slider(View):

    def __init__(self, game, size=(0.2, 0.005), handle_radius=0.01, start_value=(0, 0),
                 slide_horizontal=True, slide_vertical=False, visible=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.02,
                 frame_condition=View.NEVER, frame_thickness=0.005, corner_radius=0.01, frame_colour=BLACK,
                 bar_colour=SILVER, handle_colour=BLACK, frame_hover_colour=None, handle_hover_colour=BLUE_GREY):
        # The slider can have values between 0-1 for each axis.
        # Ensuring that the slider is centred on the axis it cannot slide, by setting value to 0.5:
        start_value = list(start_value)
        if not slide_horizontal: start_value[0] = 0.5
        if not slide_vertical: start_value[1] = 0.5

        self.slide_horizontal = slide_horizontal
        self.slide_vertical = slide_vertical
        self.value = start_value

        # The following will be set with the size:
        self.bar_rect = pygame.Rect((0, 0), (0, 0))
        self.handle_position = None

        super().__init__(game, size=size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         between=between, margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

        self.bar_colour = bar_colour

        self.handle_colour = handle_colour
        self.handle_hover_colour = handle_hover_colour

        self.handle_held = False
        self.handle_radius = self.game.unit_to_pixel(handle_radius)

    def set_size(self, size):
        # The size of the bar is the size of the element without padding:
        self.bar_rect.size = self.game.unit_to_pixel_point(size)
        super().set_size(size)

    def calculate_position(self, exclude=None):
        super().calculate_position(exclude=exclude)
        if self.bar_rect is not None:
            # Centering the slider bar:
            self.bar_rect.center = self.rect.center
            # Re-Calculating the handle position:
            self.handle_position = self.value_to_handle_position()

    def value_to_handle_position(self):
        # Converts the value of the handle into the pixel position of the handle on-screen:
        return [(self.bar_rect.left + self.value[0] * self.bar_rect.width),
                (self.bar_rect.top + self.value[1] * self.bar_rect.height)]

    def handle_position_to_value(self):
        # Converts the pixel position of the handle on-screen to its value:
        return [(self.handle_position[0] - self.bar_rect.left) / self.bar_rect.width,
                (self.handle_position[1] - self.bar_rect.top) / self.bar_rect.height]

    def update_handle_position(self):
        # Updates the position of the handle based on the mouse position:
        if self.handle_grabbed():
            self.handle_held = True
        elif self.handle_released():
            self.handle_held = False

        if self.handle_held:
            if self.slide_horizontal:
                self.handle_position[0] = pygame.mouse.get_pos()[0]
            if self.slide_vertical:
                self.handle_position[1] = pygame.mouse.get_pos()[1]
            # The position of the handle should not exceed the boundaries of the bar:
            self.handle_position[0] = max(self.handle_position[0], self.bar_rect.left)
            self.handle_position[0] = min(self.handle_position[0], self.bar_rect.right)
            self.handle_position[1] = max(self.handle_position[1], self.bar_rect.top)
            self.handle_position[1] = min(self.handle_position[1], self.bar_rect.bottom)

        # Setting the value from the updated handle position:
        self.value = self.handle_position_to_value()

    def draw_bar(self):
        pygame.draw.rect(self.display, self.bar_colour, self.bar_rect,
                         border_radius=self.corner_radius)

    def draw_handle(self, colour):
        pygame.draw.circle(self.display, colour, self.handle_position, self.handle_radius)

    def handle_grabbed(self):
        # Whether the handle has just been grabbed:
        return self.hovering() and self.game.mouse_pressed()

    def handle_is_held(self):
        return self.handle_held

    def handle_released(self):
        # Whether the handle has just been grabbed:
        return self.handle_held and self.game.mouse_released()

    def get_value(self, decimal_places=None):
        if decimal_places is None:
            return self.value
        else:
            return [round(item, decimal_places) for item in self.value]

    def hovering(self):
        mouse_pos = pygame.mouse.get_pos()
        # Using the handle's radius to see if the mouse cursor is colliding with the handle:
        return ((self.handle_position[0] - mouse_pos[0]) ** 2 + (
                self.handle_position[1] - mouse_pos[1]) ** 2) ** 0.5 <= self.handle_radius

    def draw(self):
        # Drawing frame:
        super().draw()
        # The bar colour is constant:
        self.draw_bar()
        # Drawing handle with the correct colour:
        if self.hovering(): self.draw_handle(self.handle_hover_colour)
        else: self.draw_handle(self.handle_colour)

    def update(self):
        # Updating the handle position:
        self.update_handle_position()
        super().update()


# A progress bar: [TESTED & FINALISED]
class ProgressBar(View):

    def __init__(self, game, font_size=0.03, size=(0.25, 0.025), start_progress=0,
                 orientation=View.HORIZONTAL, visible=True, show_progress_text=True,
                 position=(0, 0), above=None, below=None, to_left_of=None, to_right_of=None, between=None,
                 margin=0.02, padding=0.01,
                 frame_condition=View.ALWAYS, frame_thickness=0.005, corner_radius=0.01,
                 progress_colour=RED, frame_colour=BLACK, text_colour=PLATINUM,
                 frame_hover_colour=None, text_hover_colour=None):
        # The direction in which the progress should move:
        self.orientation = orientation

        self.progress = start_progress
        self.progress_colour = progress_colour

        # Following will be set with size:
        # We need to keep track of the max size allowed since the size of the bar can change:
        self.max_size = None
        # Tentative value (0,0), corrected afterwards:
        self.bar_rect = pygame.Rect((0, 0), (0, 0))

        # The progress text:
        self.progress_text = TextLine(game,
                                      font_size=font_size,
                                      visible=show_progress_text,
                                      frame_condition=View.NEVER,
                                      text_colour=text_colour,
                                      text_hover_colour=text_hover_colour)

        super().__init__(game, size=size, visible=visible,
                         position=position, above=above, below=below, to_left_of=to_left_of, to_right_of=to_right_of,
                         between=between,
                         margin=margin, padding=padding,
                         frame_condition=frame_condition, frame_thickness=frame_thickness, corner_radius=corner_radius,
                         frame_colour=frame_colour, frame_hover_colour=frame_hover_colour)

    def set_progress(self, progress):
        self.progress = progress
        # Setting the correct size for this progress:
        self.update_bar_size()

        # Setting the correct progress for the text:
        self.progress_text.set_text(percentage_format(progress))

        self.align_rectangles()

    def update_bar_size(self):
        if self.orientation == View.HORIZONTAL:
            self.bar_rect.width = int(self.max_size[0] * self.progress)
        else:
            self.bar_rect.height = int(self.max_size[1] * self.progress)

    def get_progress_text(self):
        return self.progress_text

    def get_progress_colour(self):
        return self.progress_colour

    def set_progress_colour(self, colour):
        self.progress_colour = colour

    def get_orientation(self):
        return self.orientation

    def set_orientation(self, orientation):
        self.orientation = orientation
        self.bar_rect.size = self.max_size
        self.set_progress(self.progress)

    def align_rectangles(self):
        self.bar_rect.topleft = self.rect.topleft + pygame.Vector2(self.padding, self.padding)
        self.progress_text.get_rect().center = self.bar_rect.center
        # Since we have moved the progress text, its position must be re-calculated for its components to be aligned:
        self.progress_text.calculate_position()

    def set_size(self, size):
        # Setting new max size:
        self.max_size = self.game.unit_to_pixel_point(size)

        # Changing the size of the bar whilst maintaining the centre:
        center = self.bar_rect.center
        self.bar_rect.size = self.max_size
        self.bar_rect.center = center

        # Updating the progress bar and text:
        self.set_progress(self.progress)
        super().set_size(size)

    def calculate_position(self, exclude=None):
        super().calculate_position(exclude)
        self.align_rectangles()

    def draw_progress(self):
        pygame.draw.rect(self.display, self.progress_colour, self.bar_rect, border_radius=self.corner_radius)

    def draw(self):
        super().draw()
        self.draw_progress()

    def update(self):
        super().update()
        self.progress_text.update()
