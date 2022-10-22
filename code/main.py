import random
import pygame
from pygame import mixer
from user_interface import *
from level import *
from strings import *
from database_helper import DatabaseHelper


# TODO: Check level-related aspects of game class:


# Main game class: [DONE]
class Game:

    def __init__(self):
        pygame.init()
        mixer.init()

        # When True, game will end:
        self.done = False

        # A helper for the relational database:
        self.database_helper = DatabaseHelper(self)

        # Getting the current resolution of the physical screen:
        screen_info = pygame.display.Info()
        self.resolution = [screen_info.current_w, screen_info.current_h]
        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)  # TODO: REMOVE
        self.rect = self.screen.get_rect()
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()

        # Calculating window dimensions - this is an arbitrary unit to make everything fully resolution independent:
        if self.resolution[0] >= self.resolution[1]:
            self.window_dimensions = [1 + self.resolution[1] / self.resolution[0], 1]
        else:
            self.window_dimensions = [1, 1 + self.resolution[1] / self.resolution[0]]

        # Setting up display:
        pygame.display.set_caption(GAME_NAME)

        # The font of the game:
        self.font = FONT
        self.all_events = []
        self.key_down_events = []

        # Creating Frame Rate Counter:
        self.fps_text = TextLine(self, font_size=0.04)

        # Initialising settings:
        self.frame_rate = None
        self.show_frame_rate = None
        self.audio_volume = None
        self.current_level = None
        self.refresh_settings()

    def refresh_settings(self):
        # Getting the frame rate cap setting from the database:
        self.frame_rate = int(self.database_helper.get_setting(DatabaseHelper.FRAME_RATE_LIMIT))

        # Getting whether the frame rate should be displayed at the corner of the screen:
        self.show_frame_rate = self.database_helper.get_setting(DatabaseHelper.SHOW_FRAME_RATE)

        # Getting the audio volume level:
        self.audio_volume = self.database_helper.get_setting(DatabaseHelper.AUDIO_VOLUME)
        mixer.music.set_volume(self.audio_volume)

        # Setting up level:
        self.update_current_level()

    def update(self):
        self.get_input()

        # Showing frame rate at the corner of the screen if enabled:
        if self.show_frame_rate:
            self.fps_text.set_text(str(int(self.clock.get_fps())))
            # Position must be recalculated every frame because the text can change:
            self.fps_text.get_rect().topleft = self.rect.topleft
            self.fps_text.draw()

    def quit(self):
        self.done = True

    def is_done(self):
        return self.done

    def get_current_level(self):
        return self.current_level

    def update_current_level(self):
        # Setting up level:
        level_id = self.database_helper.get_player_stats()[Player.CURRENT_LEVEL_ID]
        self.current_level = Level(self, level_id)

    def get_database_helper(self):
        return self.database_helper

    def get_frame_rate(self):
        return self.frame_rate

    def get_current_frame_rate(self):
        return self.clock.get_fps()

    def get_current_frame_time(self):
        frame_time = self.clock.get_fps()
        # Avoiding division by zero:
        if frame_time != 0:
            return 1 / frame_time
        else:
            return 1

    def get_frame_rate_cap(self):
        return self.frame_rate

    def set_frame_rate_cap(self, frame_rate):
        self.frame_rate = frame_rate
        # Updating the database:
        self.database_helper.update_setting(DatabaseHelper.FRAME_RATE_LIMIT, frame_rate)

    def get_show_frame_rate(self):
        return self.show_frame_rate

    def set_show_frame_rate(self, value):
        self.show_frame_rate = value
        # Updating the database:
        self.database_helper.update_setting(DatabaseHelper.SHOW_FRAME_RATE, value)

    def get_audio_volume(self):
        return self.audio_volume

    def set_audio_volume(self, audio_volume):
        # Audio value is a float between 0-1:
        self.audio_volume = audio_volume
        # Updating the database:
        self.database_helper.update_setting(DatabaseHelper.AUDIO_VOLUME, audio_volume)
        # Setting the volume of all the sounds:
        mixer.music.set_volume(audio_volume)

    def get_key_down_events(self):
        return self.key_down_events

    def get_input(self):
        self.all_events = pygame.event.get()
        self.key_down_events = []

        for event in self.all_events:
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                self.key_down_events.append(event.key)

    def key_pressed(self, key_id):
        return key_id in self.key_down_events

    def mouse_pressed(self):
        return pygame.MOUSEBUTTONDOWN in [event.type for event in self.all_events]

    def mouse_released(self):
        return pygame.MOUSEBUTTONUP in [event.type for event in self.all_events]

    def get_rect(self):
        return self.rect

    def unit_to_pixel(self, value):
        # Conversion between pixels and arbitrary units:
        return int(value * (self.resolution[0] / self.window_dimensions[0]))

    def unit_to_pixel_point(self, values):
        # Conversion between pixels and arbitrary units:
        return int(values[0] * (self.resolution[0] / self.window_dimensions[0])), \
               int(values[1] * (self.resolution[0] / self.window_dimensions[0]))

    def pixel_to_unit(self, value):
        # Conversion between pixels and arbitrary units:
        return value / (self.resolution[0] / self.window_dimensions[0])

    def pixel_to_unit_point(self, values):
        # Conversion between pixels and arbitrary units:
        return values[0] / (self.resolution[0] / self.window_dimensions[0]), \
               values[1] / (self.resolution[0] / self.window_dimensions[0])

    def get_font(self, size):
        # The size of the font in arbitrary units:
        return pygame.font.SysFont(self.font, size)

    def show_main_menu(self):
        views = []

        # <!> __UI LAYOUT__ <!>

        # Play Button:
        btn_play = Button(self,
                          text_string=PLAY_GAME,
                          position=self.rect.center)
        views.append(btn_play)

        # Settings Button:
        btn_settings = Button(self,
                              text_string=SETTINGS,
                              below=btn_play)
        views.append(btn_settings)

        # Quit Button:
        btn_quit = Button(self,
                          text_string=QUIT,
                          below=btn_settings)
        views.append(btn_quit)

        # Title Text:
        txt_title = TextLine(self,
                             text_string=GAME_NAME,
                             between=(self.rect.midtop,
                                      btn_play),
                             frame_condition=View.ALWAYS,
                             font_size=0.25)
        txt_title.set_italic(True)
        views.append(txt_title)

        # <!> __UI LAYOUT__ <!>

        while not self.done:
            self.screen.fill(WHITE)
            self.update()

            if self.key_pressed(pygame.K_1):
                self.test_1()

            # If the play button has been clicked, starting the game:
            if btn_play.clicked():
                # If the player has not played, starting player creation menu:
                if self.database_helper.get_player_stats()[Player.FULL_HEALTH] == 0:
                    self.show_information()
                    self.show_character_menu()

                # If the player has played, starting the game:
                # Not using else if, so that when character menu returns to this point, the game can start:
                if self.database_helper.get_player_stats()[Player.FULL_HEALTH] > 0:
                    self.show_game()

            elif btn_settings.clicked():
                self.show_settings_menu()
            elif self.key_pressed(pygame.K_ESCAPE):
                self.show_information()
            elif btn_quit.clicked():
                self.quit()

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_settings_menu(self):
        views = []

        # <!> __UI LAYOUT__ <!>

        # Show Frame Rate Selector:
        sel_show_frame_rate = Selector(self,
                                       font_size=0.04,
                                       start_index=int(self.show_frame_rate),
                                       position=self.rect.center,
                                       margin=0.015)
        views.append(sel_show_frame_rate)

        # Show Frame Rate Text:
        txt_show_frame_rate = TextLine(self, SHOW_FRAME_RATE,
                                       font_size=0.04,
                                       to_left_of=sel_show_frame_rate,
                                       margin=0.015)
        views.append(txt_show_frame_rate)

        # Max Frame Rate Input:
        edt_txt_frame_rate = TextInput(self,
                                       font_size=0.04,
                                       hint=str(self.frame_rate),
                                       clear_on_submit=True,
                                       input_type=TextInput.NATURAL_NUMBER,
                                       max_length=3,
                                       above=sel_show_frame_rate,
                                       margin=0.015)
        views.append(edt_txt_frame_rate)

        # Frame Rate Counter Text:
        txt_frame_rate = TextLine(self, FRAME_RATE_LIMIT,
                                  font_size=0.04,
                                  to_left_of=edt_txt_frame_rate,
                                  margin=0.015)
        views.append(txt_frame_rate)

        # Resolution Value Text:
        txt_resolution_value = TextLine(self, RESOLUTION_FORMAT.format(*self.resolution),
                                        font_size=0.04,
                                        above=edt_txt_frame_rate,
                                        frame_condition=View.ALWAYS,
                                        margin=0.015)
        views.append(txt_resolution_value)

        # Resolution Text:
        txt_resolution = TextLine(self, RESOLUTION,
                                  font_size=0.04,
                                  to_left_of=txt_resolution_value,
                                  margin=0.015)
        views.append(txt_resolution)

        # Audio Volume Slider:
        sl_audio_volume = Slider(self,
                                 below=sel_show_frame_rate,
                                 start_value=[self.audio_volume, 0],
                                 margin=0.015)
        views.append(sl_audio_volume)

        # Audio Volume Text:
        txt_audio_volume = TextLine(self, AUDIO_VOLUME,
                                    font_size=0.04,
                                    to_left_of=sl_audio_volume,
                                    margin=0.015)
        views.append(txt_audio_volume)

        # Settings Text:
        txt_settings = TextLine(self, SETTINGS,
                                between=(self.rect.midtop,
                                         txt_resolution_value.get_rect().midtop),
                                margin=0.015)
        views.append(txt_settings)

        # Delete Save Data Button:
        btn_delete_saves = Button(self, text_string=DELETE_SAVES,
                                  above=self.rect.midbottom,
                                  font_size=0.025,
                                  text_hover_colour=RED,
                                  frame_hover_colour=RED,
                                  margin=0.015)
        views.append(btn_delete_saves)

        # Back Button:
        btn_back = Button(self,
                          text_string=BACK,
                          font_size=0.04,
                          between=(sl_audio_volume.get_rect().midbottom,
                                   btn_delete_saves.get_rect().midtop),
                          margin=0.015)
        views.append(btn_back)
        # <!> __UI LAYOUT__ <!>

        while not self.done:
            self.screen.fill(WHITE)
            self.update()

            # If the frame rate has been changed and the frame rate input is not empty, setting it to the attribute:
            if edt_txt_frame_rate.submitted() and not edt_txt_frame_rate.input_empty():
                frame_rate = int(edt_txt_frame_rate.get_text())
                self.set_frame_rate_cap(frame_rate)

            # Toggling the frame rate counter if the frame rate selector is clicked:
            elif sel_show_frame_rate.clicked():
                self.set_show_frame_rate(sel_show_frame_rate.get_state() == ON)

            # If the audio volume slider has been changed, updating it:
            elif sl_audio_volume.handle_released():
                self.set_audio_volume(sl_audio_volume.get_value()[0])

            # Exit if exit button or escape clicked, returning to the previous menu:
            elif btn_back.clicked() or self.key_pressed(pygame.K_ESCAPE):
                return

            # If the delete saves button is clicked, deleting saves:
            elif btn_delete_saves.clicked():
                self.database_helper.delete_saves()
                self.refresh_settings()
                return

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_information(self):
        views = []

        # <!> __UI LAYOUT__ <!>

        # Information Text:
        txt_information = TextLine(self, INFORMATION,
                                   below=self.rect.midtop,
                                   margin=0.015)
        views.append(txt_information)

        # Information Paragraph
        txt_information_paragraph = Text(self, INFO_PARAGRAPH, font_size=0.05, below=txt_information)
        views.append(txt_information_paragraph)

        text_lines = txt_information_paragraph.get_text_lines()
        image_paths = [KEYBOARD_ICON, ATTACK_DAMAGE_ICON, SWITCH_ICON, BOTTOM_RIGHT_ARROW_ICON, CURSOR_ICON, TRASH_ICON,
                       SKULL_ICON, PAUSE_ICON, INFORMATION_ICON]

        for index, text_line in enumerate(text_lines):
            views.append(Image(self, icon=pygame.image.load(image_paths[index]), size=(0.035, 0.035),
                               to_left_of=text_line, margin=0.015, padding=0.005, frame_condition=View.ALWAYS,
                               frame_thickness=0))

        # Confirm Button:
        btn_btn_confirm = Button(self,
                                 text_string=GOT_IT,
                                 font_size=0.04,
                                 between=(txt_information_paragraph.get_rect().midbottom, self.rect.midbottom),
                                 margin=0.015)
        views.append(btn_btn_confirm)
        # <!> __UI LAYOUT__ <!>

        while not self.done:
            self.screen.fill(WHITE)
            self.update()

            # Exit if exit button or escape clicked, returning to the previous menu:
            if btn_btn_confirm.clicked() or self.key_pressed(pygame.K_ESCAPE):
                return

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_character_menu(self):
        views = []

        # <!> __UI LAYOUT__ <!>

        # Character Stats Slider:
        sl_stats = Slider(self, size=[0.3, 0.3],
                          start_value=[0.5, 0.5],
                          between=(self.rect.center, self.rect.midleft),
                          slide_horizontal=True,
                          slide_vertical=True,
                          padding=0,
                          margin=0)
        views.append(sl_stats)

        # Health Image:
        img_health = Image(self, icon=pygame.image.load(HEALTH_ICON).convert_alpha(),
                           above=sl_stats,
                           frame_condition=1)
        views.append(img_health)

        # Speed Image
        img_speed = Image(self, icon=pygame.image.load(SPEED_ICON).convert_alpha(),
                          below=sl_stats,
                          frame_condition=1)
        views.append(img_speed)

        # Attack Image:
        img_attack_damage = Image(self, icon=pygame.image.load(ATTACK_DAMAGE_ICON).convert_alpha(),
                                  to_left_of=sl_stats,
                                  frame_condition=1)
        views.append(img_attack_damage)

        # Magic Image:
        img_magic_damage = Image(self, icon=pygame.image.load(MAGIC_DAMAGE_ICON).convert_alpha(),
                                 to_right_of=sl_stats,
                                 frame_condition=1)
        views.append(img_magic_damage)

        # Initial values for stats:
        health = 1
        speed = 1
        attack = 1
        magic = 1

        # Stats Text:
        txt_stats = Text(self, CHARACTER_STATS.format(Utils.percentage_format(health),
                                                      Utils.percentage_format(speed),
                                                      Utils.percentage_format(attack),
                                                      Utils.percentage_format(magic)),
                         line_separation_ratio=0.35,
                         text_alignment=Text.CENTRE,
                         between=(self.rect.center, self.rect.midright),
                         font_size=0.065)
        views.append(txt_stats)

        # Warning Text:
        txt_warning = TextLine(self, ENTER_CHARACTER_NAME,
                               visible=False,
                               position=(0, 0),
                               font_size=0.04,
                               below=txt_stats,
                               margin=0,
                               frame_condition=View.ALWAYS,
                               text_colour=RED,
                               frame_colour=RED)
        views.append(txt_warning)

        # Continue Button:
        btn_continue = Button(self, text_string=CONTINUE,
                              below=txt_warning)
        views.append(btn_continue)

        # Character Name Input:
        edt_txt_player_name = TextInput(self,
                                        max_length=20,
                                        hint=CHARACTER_NAME,
                                        above=txt_stats)
        views.append(edt_txt_player_name)

        # <!> __UI LAYOUT__ <!>

        while not self.done:
            self.screen.fill(WHITE)
            self.update()

            if self.key_pressed(pygame.K_ESCAPE):
                return

            # If the player is adjusting the stats, updating the stats text:
            elif sl_stats.handle_held:
                slider_value = sl_stats.get_value()
                health = round(Player.MIN_HEALTH + (Player.MAX_HEALTH - Player.MIN_HEALTH) * (1 - slider_value[1]), 2)
                speed = round(Player.MIN_SPEED + (Player.MAX_SPEED - Player.MIN_SPEED) * slider_value[1], 2)
                magic = round(Player.MIN_MAGIC + (Player.MAX_MAGIC - Player.MIN_MAGIC) * slider_value[0], 2)
                attack = round(Player.MIN_ATTACK + (Player.MAX_ATTACK - Player.MIN_ATTACK) * (1 - slider_value[0]), 2)
                txt_stats.set_text(CHARACTER_STATS.format(Utils.percentage_format(health),
                                                          Utils.percentage_format(speed),
                                                          Utils.percentage_format(attack),
                                                          Utils.percentage_format(magic)))

            elif btn_continue.clicked():
                if edt_txt_player_name.input_empty():
                    # If the player has not entered a name, showing a warning:
                    txt_warning.set_visibility(True)
                else:
                    # If the player has entered a name, saving the character
                    # and returning to the main menu which will start the game:
                    self.database_helper.update_player_stats({Player.FULL_HEALTH: health,
                                                              Player.CURRENT_HEALTH: health,
                                                              Player.SPEED_MULTIPLIER: speed,
                                                              Player.MELEE_DAMAGE_MULTIPLIER: attack,
                                                              Player.MAGIC_DAMAGE_MULTIPLIER: magic})
                    return

            elif txt_warning.clicked():
                # If the player clicks on the warning, hiding it:
                txt_warning.set_visibility(False)

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_game(self):
        background_colour = self.current_level.get_background_colour()

        # Map needs to be set up after we have correct player from player creation menu:
        self.current_level.set_up_map()
        player = self.current_level.get_player()

        views = []

        # Pause button:
        btn_pause = Button(self, icon=pygame.image.load(PAUSE_ICON).convert_alpha(),
                           size=(0.05, 0.05),
                           padding=0.01,
                           frame_condition=View.ALWAYS)
        btn_pause.get_rect().topright = self.rect.topright + pygame.Vector2(-btn_pause.get_margin(),
                                                                            btn_pause.get_margin())
        views.append(btn_pause)

        # Switch item button:
        btn_switch = Button(self, icon=pygame.image.load(SWITCH_ICON).convert_alpha(),
                            size=(0.05, 0.05),
                            padding=0.01,
                            frame_condition=View.ALWAYS)
        btn_switch.get_rect().midright = self.rect.midright + pygame.Vector2(-btn_switch.get_margin(), 0)
        views.append(btn_switch)

        # Use item button:
        btn_use = Button(self, icon=player.get_item_selected().get_icon(),
                         below=btn_switch,
                         size=(0.05, 0.05),
                         padding=0.01,
                         frame_condition=View.ALWAYS)
        views.append(btn_use)

        # Item properties text:
        txt_item = Text(self, player.get_item_selected().properties(player),
                        text_alignment=View.CENTRE,
                        font_size=0.02,
                        padding=0.0075,
                        frame_thickness=0,
                        text_colour=WHITE,
                        frame_colour=BLACK)
        margin = txt_item.get_margin()
        txt_item.get_rect().bottomright = self.rect.bottomright + pygame.Vector2(-margin, -margin)
        # Need tp re-position the texts since we are modifying the
        # location of the element without using the methods directly:
        txt_item.position_texts()
        views.append(txt_item)

        # Health bar:
        pr_health = ProgressBar(self, to_left_of=btn_pause)
        views.append(pr_health)

        # Information Button:
        btn_information = Button(self, icon=pygame.image.load(INFORMATION_ICON).convert_alpha(),
                                 to_left_of=pr_health,
                                 size=(0.025, 0.025),
                                 margin=0,
                                 padding=0.0075,
                                 frame_thickness=0.0045,
                                 frame_condition=View.ALWAYS)
        views.append(btn_information)

        # Trash Button:
        btn_trash = Button(self, icon=pygame.image.load(TRASH_ICON).convert_alpha(),
                           to_left_of=btn_use,
                           size=(0.025, 0.025),
                           margin=0,
                           padding=0.0075,
                           frame_thickness=0.0045,
                           frame_condition=View.ALWAYS)
        views.append(btn_trash)

        while (not self.done) and (not self.current_level.is_done()):
            self.screen.fill(background_colour)
            self.current_level.update()

            # Go to main menu if paused:
            if self.key_pressed(pygame.K_ESCAPE) or btn_pause.clicked(): return

            # Increment item selected:
            if self.key_pressed(pygame.K_TAB) or btn_switch.clicked():
                player.increment_item_selected()
                # After switching item, the icon and text need to be updated:
                btn_use.set_icon(player.get_item_selected().get_icon())
                txt_item.set_text(player.get_item_selected().properties(player))

            # Use item:
            if btn_use.clicked():
                player.use_item()

            elif btn_information.clicked():
                self.show_information()
            elif btn_trash.clicked():
                pass
                # TODO: REMOVE ITEM SELECTED

            # For testing TODO: REMOVE:
            if pr_health.clicked():
                player.receive_damage(0.05)

            # Have Player.health_changed() to return true.
            pr_health.set_progress(player.get_stats()[Player.CURRENT_HEALTH] / player.get_stats()[Player.FULL_HEALTH])

            for view in views: view.update()
            # Putting update at the bottom so the FPS counter is always visible:
            self.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        # After a level is done, update:
        if not self.done:
            self.update_current_level()
            self.show_game()

    def show_death_screen(self):
        views = []
        btn_continue = Button(self, text_string=CONTINUE,
                              position=self.rect.center,
                              text_colour=PLATINUM)
        views.append(btn_continue)

        txt_died = TextLine(self, YOU_DIED,
                            font_size=0.2,
                            above=btn_continue,
                            text_colour=RED)
        views.append(txt_died)

        btn_quit = Button(self, QUIT,
                          below=btn_continue,
                          text_colour=PLATINUM)
        views.append(btn_quit)

        while not self.done:
            self.screen.fill(BLACK)
            self.update()

            # Go back to the level:
            if self.key_pressed(pygame.K_ESCAPE) or btn_continue.clicked(): return

            elif btn_quit.clicked(): self.done = True

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def test_1(self):
        views = []
        example_texts = []

        txt_test = TextLine(self, "Testing Responsive Rendering", font_size=0.05,
                            frame_condition=View.ALWAYS,
                            margin=0.05, padding=0.03)
        txt_test.get_rect().midtop = self.rect.midtop + pygame.Vector2(0, txt_test.get_margin())
        views.append(txt_test)
        example_texts.append(txt_test)

        edt_txt_1 = TextInput(self, hint="Type Something Here!", font_size=0.05,
                              corner_radius=1, frame_thickness=0.004,
                              max_length=15, clear_on_submit=True,
                              below=txt_test, margin=0.05)
        views.append(edt_txt_1)
        example_texts.append(edt_txt_1)

        sl_text_size = Slider(self, below=edt_txt_1, margin=0.015)
        views.append(sl_text_size)

        pr_test = ProgressBar(self, below=sl_text_size, margin=0.015)
        views.append(pr_test)

        sl_padding = Slider(self, below=pr_test, margin=0.015)
        views.append(sl_padding)

        sl_margin = Slider(self, below=sl_padding, margin=0.015)
        views.append(sl_margin)

        txt_paragraph = Text(self, text_string="Hi\nThere\nHow\nAre\nYou\nToday?", font_size=0.02,
                             to_right_of=edt_txt_1)
        views.append(txt_paragraph)
        example_texts.append(txt_paragraph)

        btn_centre = Button(self, text_string="Centre", font_size=0.02, to_right_of=txt_paragraph, margin=0.005,
                            padding=0.007, frame_thickness=0.0025)
        views.append(btn_centre)

        btn_left = Button(self, text_string="Left", font_size=0.02, above=btn_centre, margin=0.005,
                          padding=0.007, frame_thickness=0.0025)
        views.append(btn_left)

        btn_right = Button(self, text_string="Right", font_size=0.02, below=btn_centre, margin=0.005,
                           padding=0.007, frame_thickness=0.0025)
        views.append(btn_right)

        btn_underline = Button(self, text_string="U", font_size=0.03, below=sl_margin, underline=True, margin=0.015)
        views.append(btn_underline)

        btn_bold = Button(self, text_string="B", font_size=0.03, to_left_of=btn_underline, bold=True, margin=0.015)
        views.append(btn_bold)

        btn_italic = Button(self, text_string="I", font_size=0.03, to_right_of=btn_underline, italic=True, margin=0.015)
        views.append(btn_italic)

        btn_back = Button(self, text_string="Back", font_size=0.03, between=(btn_underline, self.rect.midbottom),
                          margin=0.015)
        views.append(btn_back)

        while not self.done:
            self.screen.fill(WHITE)
            self.update()

            if self.key_pressed(pygame.K_ESCAPE): return

            if sl_text_size.handle_is_held():
                for text in example_texts:
                    text.set_font_size(0.05 + 0.03 * sl_text_size.get_value()[0])
                txt_paragraph.set_font_size(0.02 + 0.02 * sl_text_size.get_value()[0])
                pr_test.set_progress(sl_text_size.get_value()[0])

            elif pr_test.clicked():
                pr_test.set_progress_colour(random.choice([RED, GREEN, BLUE, CYAN, MAGENTA, MAROON, IRIS]))
            elif btn_left.clicked():
                txt_paragraph.set_alignment(Text.LEFT)
            elif btn_centre.clicked():
                txt_paragraph.set_alignment(Text.CENTRE)
            elif btn_right.clicked():
                txt_paragraph.set_alignment(Text.RIGHT)

            elif btn_bold.clicked():
                for text in example_texts:
                    text.set_bold(not text.get_bold())
                btn_bold.set_frame_condition([View.HOVER, View.ALWAYS][example_texts[0].get_bold()])

            elif btn_italic.clicked():
                for text in example_texts:
                    text.set_italic(not text.get_italic())
                btn_italic.set_frame_condition([View.HOVER, View.ALWAYS][example_texts[0].get_italic()])

            elif btn_underline.clicked():
                for text in example_texts:
                    text.set_underline(not text.get_underline())
                btn_underline.set_frame_condition([View.HOVER, View.ALWAYS][example_texts[0].get_underline()])

            elif btn_back.clicked(): return

            for view in views: view.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)


if __name__ == "__main__":
    Game().show_main_menu()
