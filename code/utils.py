import pygame
from os import walk


# Miscellaneous functions: [DONE]
class Utils:

    @staticmethod
    # Places all image surfaces in a directory into a list:
    def import_images_from_folder(path):


        images = []

        for _, __, image_files in walk(path):
            # The data_item variable contains a tuple with the following items:
            #   0: path to the folder
            #   1: List of folders in path
            #   2: list of files in our current path <- We are only interested in this.

            # The image variable will be a string of the file name:
            for image_file in image_files:
                # The full path to reach the image:
                full_path = path + "/" + image_file

                # Creating a surface using the image retrieved:
                image_surface = pygame.image.load(full_path).convert_alpha()
                images.append(image_surface)

        return images

    @staticmethod
    # Resizes an image whilst protecting the aspect ratio:
    def resize_image(image, size):
        current_image_size = image.get_size()
        width = current_image_size[0]
        height = current_image_size[1]

        if width > height:
            scale_factor = size[0] / width
            width = size[0]
            height *= scale_factor
        else:
            scale_factor = size[1] / height
            height = size[1]
            width *= scale_factor

        return pygame.transform.scale(image, (width, height))

    @staticmethod
    def percentage_format(float_value):
        return "{}%".format(int(float_value * 100))
