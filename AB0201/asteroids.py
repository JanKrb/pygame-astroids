"""A simple desktop game implemented with Pygame.

Credits:
 * Sprites: 
 * Sound: 
"""
import os
from math import copysign, cos, radians, sin
from typing import Any, Dict, Tuple

import pygame
from pygame.constants import K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP, QUIT

from mytools import SpriteContainer, Timer


class Settings:
    """Project global informations"""

    window = {"width": 1200, "height": 700}
    fps = 60
    path: Dict[str, str] = {}
    path["file"] = os.path.dirname(os.path.abspath(__file__))
    path["image"] = os.path.join(path["file"], "images")
    path["sound"] = os.path.join(path["file"], "sounds")
    caption = 'Fingerübung "Asteroids"'
    playground = pygame.Rect(0, 0, window["width"], window["height"] - 50)
    d_angle = 22.5

    @staticmethod
    def get_dim() -> Tuple[int, int]:
        """Dimensions of the screen.
        Returns:
            (int, int): Width and height of the window.
        """
        return (Settings.window["width"], Settings.window["height"])

    @staticmethod
    def get_file(filename: str) -> str:
        """Full path of the a file in the home directory of the game.

        Args:
            filename (str): Name of the file

        Returns:
            str: Absolute path with filename of the file
        """
        return os.path.join(Settings.path["file"], filename)

    @staticmethod
    def get_image(filename: str) -> str:
        """Full path of the image file.

        Args:
            filename (str): Name of the file

        Returns:
            str: Absolute path with filename of the image file
        """
        return os.path.join(Settings.path["image"], filename)

    @staticmethod
    def get_sound(filename: str) -> str:
        """Full path of the sound file.

        Args:
            filename (str): Name of the file

        Returns:
            str: Absolute path with filename of the sound file
        """
        return os.path.join(Settings.path["sound"], filename)


class Background(pygame.sprite.Sprite):
    """Sprite class with nearly no function for drawing the background image."""

    def __init__(self, filename: str = "background.png") -> None:
        """Constructor.

        Args:
            filename (str, optional): Filename of the background image. Defaults to "background.png".
        """
        super().__init__()
        self.image = pygame.image.load(Settings.get_image(filename)).convert()
        self.image = pygame.transform.scale(self.image, Settings.get_dim())
        self.rect = self.image.get_rect()


class Ship(pygame.sprite.Sprite):
    """Ship sprite class."""

    def __init__(self) -> None:
        """Constructor"""
        super().__init__()
        self._mode = 0  # 0 = flying, 1 = accelerating
        self.images = Game.Sprite_container.get_sprites("ships_flying")
        self.imageindex = 0
        self.image: pygame.surface.Surface = self.images[self.imageindex]
        self.mask = pygame.mask.from_surface(self.image)

        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = Settings.playground.center
        self._timer_acc = Timer(100)
        self._angle = 0
        self.speed_x = 0
        self.speed_y = 0

    def get_angle(self) -> float:
        """Converts the angle from grad to radiant.

        Returns:
            float: radiant of the angle
        """
        return radians(self._angle)

    def _set_mode(self, mode: int) -> None:
        """Determines whether the ship is flying or accelerating.

        Args:
            mode (int): 0 = flying, 1 = accelerating
        """
        self._mode = mode
        if mode == 0:
            self.images = Game.Sprite_container.get_sprites("ships_flying")
        elif mode == 1:
            self.images = Game.Sprite_container.get_sprites("ships_acc")

    def _rotate(self, direction: int) -> None:
        """Shifts the angle of the ship.

        Sets the new angle, changes the image, and creates the new mask.

        Args:
            direction (int): -1 = rotate left, +1 rotate right
        """
        self._angle += copysign(Settings.d_angle, direction)
        self._angle %= 360
        self.imageindex += direction
        self.imageindex %= len(self.images)
        self.image = self.images[self.imageindex]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Main update function of the sprite.

        The method controls which behaviour of the sprite changes:

        Args:
            direction (int): -1 = rotate left, +1 rotate right
            mode (int): 0 = flying, 1 = accelerating
            go (bool): True = update of speed and position
        """
        if "direction" in kwargs.keys():
            self._rotate(kwargs["direction"])
        if "mode" in kwargs.keys():
            self._set_mode(kwargs["mode"])
        if "go" in kwargs.keys():
            if kwargs["go"]:
                self.image = self.images[self.imageindex]
                if self._mode == 1:
                    if self._timer_acc.is_next_stop_reached():  # Beschleunigung verlangsamen
                        angle = radians(self._angle)
                        newspeed_x = self.speed_x - sin(angle)  # Geschwindigkeit begrenzen
                        newspeed_y = self.speed_y - cos(angle)
                        if abs(newspeed_x) < 10 and abs(newspeed_y) < 10:
                            self.speed_x = newspeed_x
                            self.speed_y = newspeed_y
                self.rect.move_ip(self.speed_x, self.speed_y)
                if self.rect.right < 0:
                    self.rect.left = Settings.playground.width
                if self.rect.left > Settings.playground.width:
                    self.rect.right = 0
                if self.rect.bottom < 0:
                    self.rect.top = Settings.playground.height
                if self.rect.top > Settings.playground.height:
                    self.rect.bottom = 0

    def draw(self, surface: pygame.surface.Surface) -> None:
        """Blits the image on the surface.

        Args:
            surface (pygame.surface.Surface): Target of the blit operation.
        """
        surface.blit(self.image, self.rect)


class Game:
    """The class Game is the main starting class of the game."""

    Sprite_container: SpriteContainer

    def __init__(self) -> None:
        """Constructor"""
        pygame.init()
        self._screen = pygame.display.set_mode(Settings.get_dim())
        pygame.display.set_caption(Settings.caption)
        self._clock = pygame.time.Clock()

        Game.Sprite_container = SpriteContainer(
            Settings.get_file("sprites.json"), Settings.get_image("spritesheet.bmp"), (0, 0, 0)
        )
        self._background = pygame.sprite.GroupSingle(Background("background_black.png"))
        self._ship = Ship()
        self._running = True

    def watch_for_events(self) -> None:
        """Looking for any type of event and poke a reaction."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self._running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self._running = False
                elif event.key == K_UP:
                    self._ship.update(mode=1)
                elif event.key == K_LEFT:
                    self._ship.update(direction=1)
                elif event.key == K_RIGHT:
                    self._ship.update(direction=-1)
            elif event.type == KEYUP:
                if event.key == K_UP:
                    self._ship.update(mode=0)

    def draw(self) -> None:
        """Draws all sprite on the screen."""
        self._background.draw(self._screen)
        self._ship.draw(self._screen)
        pygame.display.flip()

    def update(self) -> None:
        """This method is responsible for the main game logic."""
        if self._running:
            self._ship.update(go=True)

    def run(self) -> None:
        """Starting point and main loop of the game."""
        self._running = True
        while self._running:
            self._clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    os.environ["SDL_VIDEO_WINDOW_POS"] = "10, 30"
    game = Game()
    game.run()
