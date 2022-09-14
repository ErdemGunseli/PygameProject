import pygame
from os import walk


class Utils:

    @staticmethod
    def import_folder(path):
        # Pygame needs to be initiated for this function to work:

        surface_list = []

        for _, __, image_files in walk(path):
            # The data_item variable contains a tuple.
            # 0: path,
            # 1: List of folders in path
            # 2: list of files in our current path

            # The image variable will be a string of the file name:
            for image_file in image_files:
                # The full path to reach the image:
                full_path = path + "/" + image_file

                # Creating a surface using the image retrieved:
                image_surface = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surface)

        return surface_list

    @staticmethod
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
