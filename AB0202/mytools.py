import json
from typing import Tuple

import pygame


class Timer:
    """Timer in order to check time periodes."""

    def __init__(self, duration: int, with_start: bool = True) -> None:
        """Constructor

        Args:
            duration (int): duration of the time interval in milli seconds
            with_start (bool, optional): Controls if the first period will count (True) or not (False). Defaults to True.
        """
        self.duration = duration
        if with_start:
            self._next = pygame.time.get_ticks()
        else:
            self._next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self) -> bool:
        """Checks if the end of a time period is reached or exceeded.

        Returns:
            bool: True if the end of the period is reached or exceeded; otherwise False
        """
        if pygame.time.get_ticks() > self._next:
            self._next = pygame.time.get_ticks() + self.duration
            return True
        return False


class Animation:
    """This class helps to animate a sprite."""

    def __init__(self, namelist: list[str], endless: bool, animationtime: int, colorkey: Tuple[int, int, int] = None):
        """Constructor.

        Args:
            namelist (list[str]): List of filenames of the picures of the animation. The order of the filenames is the order of the animation.
            endless (bool): True = animation repeats endless. False = animation stops after the last picture.
            animationtime (int): milliseconds between each picture.
            colorkey (Tuple[int, int, int], optional): Transparent color. Defaults to None. If this color is not set, the transparancy must be coded by the picture itself.
        """
        self.images: list[pygame.surface.Surface] = []
        self.endless = endless
        self.timer = Timer(animationtime)
        for filename in namelist:
            if colorkey == None:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert_alpha()
            else:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert()
                bitmap.set_colorkey(colorkey)
            self.images.append(bitmap)
        self.imageindex = -1

    def next(self) -> pygame.surface.Surface:
        """Computes the next animation picure.

        Returns:
            pygame.surface.Surface: Next picure of the animation.
        """
        if self.timer.is_next_stop_reached():
            self.imageindex += 1
            if self.imageindex >= len(self.images):
                if self.endless:
                    self.imageindex = 0
                else:
                    self.imageindex = len(self.images) - 1
        return self.images[self.imageindex]

    def is_ended(self) -> bool:
        """Checks wether the animation has reached the end or not.

        Returns:
            bool: True = end is reached, otherwise False.
        """
        if self.endless:
            return False
        elif self.imageindex >= len(self.images) - 1:
            return True
        else:
            return False


class SpriteContainer:
    def __init__(self, rectfile: str, spritesheetfile: str, colorkey: Tuple[int, int, int] = None) -> None:
        self._spritesheed = pygame.image.load(spritesheetfile).convert()
        if colorkey == None:
            self._spritesheed = self._spritesheed.convert_alpha()
        else:
            self._spritesheed = self._spritesheed.convert()
            self._spritesheed.set_colorkey(colorkey)
        self._rects: dict[str, dict[int, pygame.Rect]] = {}
        self._sprites: dict[str, dict[int, pygame.surface.Surface]] = {}
        self._load(rectfile)

    def _load(self, filename: str) -> None:
        """Loads the json-file which defines the sprites in a spritesheet.

        The json file has the following structure:
        '{
            <name of the sprite sequence>:{<index>:[<left>, <top>, <width>, <height>], ...},
            ...,
            <name of the sprite sequence>:{<index>:[<left>, <top>, <width>, <height>], ...},
        }'
        Args:
            filename (str): Name of the json file.
        """
        with open(filename) as infile:
            data = json.load(infile)
            for spritename in data.items():
                self._rects[spritename[0]] = {}
                self._sprites[spritename[0]] = {}
                for rectdata in spritename[1].items():
                    index = int(rectdata[0])
                    self._rects[spritename[0]][index] = pygame.Rect(
                        rectdata[1][0], rectdata[1][1], rectdata[1][2], rectdata[1][3]
                    )
                    self._sprites[spritename[0]][index] = self._spritesheed.subsurface(
                        self._rects[spritename[0]][index]
                    )

    def get_sprites(self, key: str) -> dict[int, pygame.surface.Surface]:
        """Returns a sprite sequence.

        Args:
            key (str): Name of the sprite sequence

        Returns:
            dict[int, pygame.surface.Surface]: sprite sequence
        """
        return self._sprites[key]
