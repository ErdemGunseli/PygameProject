from main import *
import unittest
from unittest.mock import patch


class TestView(unittest.TestCase):

    # Note that the class method decorator means that the method is that of the class, not the instance.
    # This differs from the static method decorator because it has access to the class itself via cls.
    # Runs before any tests begin:
    @classmethod
    def setUpClass(cls):
        pass

    # Runs after all tests end:
    # Not needed for this unit test.
    @classmethod
    def tearDownClass(cls):
        pass

    # Runs before each test:
    def setUp(self):
        # Each View object needs a game instance:
        self.game = Game()

        # For this test, the game class will be modified slightly to not detect the resolution of the display
        # (this will be tested separately) and a fixed resolution of 1000x1000 will be used in windowed mode
        # so that the test data values are simpler.

        # Since the View class is abstract, we can utilise any of the children
        # to test for the core functionality of the parent class.

        # Using a layout with an image at the centre, and a line of text underneath:
        self.image = Image(self.game, pygame.image.load(HEALTH_ICON).convert_alpha(),
                           size=(1, 1), position=self.game.get_rect().center, padding=0)
        self.text_line = TextLine(self.game, "Sample", below=self.image)

    # Runs after each test:
    # Not needed for this unit test.
    def tearDown(self):
        pass

    def test_set_size(self):
        # Testing that the size of the view element is set correctly:

        # Test data list where each element is a list of 2 tuples:
        #   1. The size of the element to be set
        #      (as a proportion of the screen size where 1=100% of the smaller screen size)
        #   2. The expected size of the view in pixels
        test_data = [[(1, 1), (1000, 1000)],
                     [(0.5, 0.5), (500, 500)],
                     [(0, 0), (500, 500)],  # Order of this test relative to the others is important
                     [(1.5, 1), (1500, 1000)],
                     [(1, 0.5), (1000, 500)],
                     [(0.5, 1), (500, 1000)],
                     [(0.34, 0.57), (340, 570)],
                     [(1.5, 0.05), (1500, 50)],
                     [(0.9, 0.9), (900, 900)],
                     [(2.43, 3.45), (2430, 3450)]
                     ]

        print("\n\033[1mUnit Test for View.set_size():")
        for index, test in enumerate(test_data):
            print(f"\tTest {index + 1} of {len(test_data)} \t{'%30s' % test} :", end="\t\t")
            # Setting the size of the image element from the test data:
            self.image.set_size(test[0])
            # Testing if the actual size (calculated from the arguments) is correct:
            self.assertEqual(self.image.rect.size, test[1])
            print(f"\033[92m\033[1mPassed")
        print("\n")

    def test_calculate_position(self):
        # Testing that related view elements are shifted by the correct amount when the size of one of them is changed:
        # (Purpose of this feature is to achieve responsive rendering and avoid UI elements from overlapping)

        # Changing the size of the image to a range of valid values and testing if the text line shifts away by the
        # correct amount to prevent the elements from overlapping:

        # Recording the initial y position of the TextLine object so that it can be compared to its final position:
        #  (the x position should not change since the text line is below the image - only needs to move up/down)
        initial_y = self.text_line.rect.centery

        # Test data list where each element is a list of 2 values:
        #   1. The new height of the image as a proportion of the screen size (where 1=100%)
        #   2. The expected change in the y position of the text line
        test_data = [[1, 0],
                     [3, 1000],
                     [0.1, -450],
                     [0.51, -245],
                     [1.8, 400],
                     [0.24, -380],
                     [0.78, -110],
                     [1.90, 450],
                     [1.44, 220],
                     [6.90, 2950]
                     ]

        print("\n\033[1mUnit Test for View.calculate_position():")
        for index, test in enumerate(test_data):
            print(f"\tTest {index + 1} of {len(test_data)} \t{'%30s' % test} :", end="\t\t")
            # Setting the size of the image element from the test data causes the calculate_position method to be run
            # which should automatically cause the text line to move out of the way as the size of the image changes:
            self.image.set_size((1, test[0]))
            # Testing if the text line has moved by the correct amount:
            delta_y = self.text_line.rect.centery - initial_y
            self.assertEqual(delta_y, test[1])
            print(f"\033[92m\033[1mPassed")
        print("\n")

    def test_hovering(self):
        # Testing that the UI element can correctly detect when the user hovers over it with the mouse:

        # Changing the position of the mouse to a range of valid values and testing if the element can detect if the
        # mouse is hovering over it:

        # Test data list where each element is a list of 2 elements:
        #   1. The pixel coordinates of the position of the mouse (artificially set through mocking)
        #   2. Whether the mouse is expected to be hovering over the element (True/False)
        test_data = [[(500, 500), True],
                     [(-1, -1), False],
                     [(0, 0), True],
                     [(1001, 1001), False],
                     [(999, 999), True],
                     [(1000, 1000), False],
                     [(987, 1001), False],
                     [(-1000, 0), False],
                     [(0, -1000), False],
                     [(350, 350), True]
                     ]

        print("\n\033[1mUnit Test for View.hovering():")
        for index, test in enumerate(test_data):
            print(f"\tTest {index + 1} of {len(test_data)} \t{'%30s' % test} :", end="\t\t")
            # Mocking the position of the mouse so that it can be tested without actually moving the mouse:
            with patch('pygame.mouse') as mock_mouse:
                mock_mouse.get_pos = lambda: test[0]
                self.assertIs(self.image.hovering(), test[1])
            print(f"\033[92m\033[1mPassed")
        print("\n")


class TestPlayer(unittest.TestCase):

    def setUp(self):
        # Each Character object needs a game instance:
        self.game = Game()

        # Creating a level to test the player on:
        self.level = Level(self.game, 1)
        self.game.current_level = self.level
        self.level.set_up_map()

        # Creating a player & enemy object to test:
        self.player = self.level.get_player()
        self.enemy = Utils().get_enemy(self.game, DEMON)

    def test_collision(self):
        # Testing that the player can correctly detect when it is colliding with another object
        # and is unable to move into the object:

        # (Note that since the collision method is in the character class which is inherited by Player and Enemy,
        # so this test applies to both of these classes)

        # Changing the position and direction of the player to a range of valid values
        # to test if collision is correctly detected and handled:

        # Test data list where each element is a list of 3 elements:
        #   1. The pixel coordinate of the player
        #   2. Whether a collision is expected in the x and/or y axes
        test_data = [[(196, 450), True],
                     [(1000, 150), False],
                     [(1050, 149), True],
                     [(900, 155), False],
                     [(1500, 500), False],
                     [(346, 388), True],
                     [(2825, 2630), True],
                     [(1138, 1115), False],
                     [(191, 2702), True],
                     [(2438, 690), True],
                     ]

        print("\n\033[1mUnit Test for Character.handle_collision():")
        for index, test in enumerate(test_data):
            print(f"\tTest {index + 1} of {len(test_data)} \t{'%30s' % test} :", end="\t\t")
            # Normally, the player only checks collision with tiles that are visible on-screen.
            # For this test, we are not concerned with the screen,
            # so setting the tiles visible on-screen as all the tiles:
            self.player.level.get_obstacle_tiles_in_frame = lambda: self.level.obstacle_tiles
            self.player.collider.center = test[0]
            collision = self.player.handle_collision(0) or self.player.handle_collision(1)
            self.assertIs(collision, test[1])
            print(f"\033[92m\033[1mPassed")


if __name__ == '__main__':
    unittest.main()
