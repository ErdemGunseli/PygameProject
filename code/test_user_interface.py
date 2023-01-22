import random
from user_interface import *
from assets import *
import pygame
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

        # Obtaining the resolution since it is necessary for a lot of the validation:
        self.resolution = self.game.resolution
        print(f"Screen Resolution Detected As: {self.resolution}")
        self.window_dimensions = self.game.window_dimensions

        # Since the View class is abstract, we can utilise any of the children
        # to test for the core functionality of the parent class.

        # Using a layout with an image at the centre, and a line of text underneath:
        self.image = Image(self.game, pygame.image.load(HEALTH_ICON).convert_alpha(),
                           position=self.game.get_rect().center)
        self.text_line = TextLine(self.game, "Sample", below=self.image, )

        pass

    # Runs after each test:
    # Not needed for this unit test.
    def tearDown(self):
        pass

    def test_set_size(self):
        # Testing that the size of the view is set correctly for 1000 random valid values:
        for i in range(1000):
            # Remember that the sizes of UI elements are set as a proportion of the screen (0.01=1%, 1=100%):
            width = random.uniform(0.01, 1)
            height = random.uniform(0.01, 1)
            self.image.set_size((width, height))
            self.assertEqual(
                self.image.get_rect().size,
                # The following is what the size should be:
                tuple([int(dimension * (self.resolution[0] / self.window_dimensions[0])) +
                       2 * self.image.get_padding() for dimension in (width, height)]))

    def test_calculate_position(self):
        # Changing the size of the image for 1000 valid values and testing if the
        # text line shifts away by the correct amount to prevent the elements from overlapping
        # and the margin amounts are maintained:
        for i in range(1000):
            width = random.uniform(0.01, 1)
            height = random.uniform(0.01, 1)
            self.image.set_size((width, height))

            # The text line should automatically be moved below the image again,
            # rather than overlapping, taking into account the margins of the elements:
            self.assertEqual(
                self.image.get_rect().bottom,
                self.text_line.get_rect().top - self.text_line.get_margin() - self.image.get_padding())

    def test_hovering(self):
        for i in range(1000):
            # Mocking the position of the mouse:
            with patch('pygame.mouse') as mock_mouse:
                mock_mouse_pos = [random.randint(0, self.resolution[i]) for i in range(2)]
                mock_mouse.get_pos = lambda: mock_mouse_pos
                print(mock_mouse_pos)



                rect = self.image.get_rect()
                hovering = (rect.left < mock_mouse_pos[0] < rect.right) and (rect.top < mock_mouse_pos[1] < rect.bottom)
                print(f"{self.image.hovering()} = {hovering}")

                self.assertIs(self.image.hovering(), hovering)



        pass

    def test_clicked(self):
        pass


if __name__ == '__main__':
    unittest.main()
