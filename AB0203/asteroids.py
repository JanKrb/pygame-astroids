"""A simple desktop game implemented with Pygame.

Credits:
 * Sprites: 
 * Sound: 
"""
import os
from math import copysign, cos, radians, sin
from random import randint
from typing import Any, Dict, Tuple

import pygame
from pygame.constants import (K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP,
                              QUIT, K_KP_ENTER, K_RETURN)

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
    max_big_rocks = 5
    rock_intervall = 300
    bullet_ttl = 5000
    max_bullets = 10
    bullet_min_speed = 3

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


class Background(pygame.sprite.DirtySprite):
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
        self.dirty = 1
    
    def draw(self, screen):
        screen.blit(self.image, (0, 0))

class Ship(pygame.sprite.DirtySprite):
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

        self.dirty = 1

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
        self.dirty = 1

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
        self.dirty = 1

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
        if "shoot" in kwargs.keys():
            self.shoot()
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
                self.dirty = 1
    
    def shoot(self):
        if len(game._bullets) < Settings.max_bullets:
            game._bullets.add(Bullet(self._angle, (self.speed_x, self.speed_y), self.rect.center))

    def draw(self, surface: pygame.surface.Surface) -> None:
        """Blits the image on the surface.

        Args:
            surface (pygame.surface.Surface): Target of the blit operation.
        """
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.DirtySprite):
    """Bullet sprite class"""

    def __init__(self, angle, speed, pos) -> None:
        super().__init__()

        self.angle = angle
        self.speed = self.calculate_speed(speed)
        self.pos = pos
        self.life_timer = Timer(Settings.bullet_ttl, False)
        self.image = Game.Sprite_container.get_sprites("bullets")[2]
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect.center = self.pos

        self.dirty = 1
    
    def calculate_speed(self, speed):
        new_speed = { 'x': 0, 'y': 0 }
        angle = radians(self.angle)

        new_speed['x'] = speed[0] - sin(angle)
        new_speed['y'] = speed[1] - cos(angle)

        if new_speed['x'] > 0 and new_speed['x'] < Settings.bullet_min_speed:
            new_speed['x'] = Settings.bullet_min_speed

        elif new_speed['x'] < 0 and new_speed['x'] > -Settings.bullet_min_speed:
            new_speed['x'] = -Settings.bullet_min_speed

        if new_speed['y'] > 0 and new_speed['y'] < Settings.bullet_min_speed:
            new_speed['y'] = Settings.bullet_min_speed

        elif new_speed['y'] < 0 and new_speed['y'] > -Settings.bullet_min_speed:
            new_speed['y'] = -Settings.bullet_min_speed

        return new_speed
    
    def update(self):
        if self.life_timer.is_next_stop_reached():
            self.kill()
        self.move()
    
    def move(self):
        self.rect.move_ip(self.speed['x'], self.speed['y'])
        self.dirty = 1
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
class Rock(pygame.sprite.DirtySprite):
    """Rock sprite class"""

    def __init__(self, size : str ="big") -> None:
        """Constructor 

        Args:
            size (str, optional): defines the size of the rock. Possible are "big", "medium", "small", and "large". Defaults to "big".
        """
        super().__init__()
        self.speed = 0
        if size == "big":
            self.speed = -3.0
            index = 0
        elif size == "medium":
            index = randint(1, 2)
            self.speed = -4
        elif size == "small":
            index = randint(3, 5)
            self.speed = -4
        elif size == "tiny":
            self._points = 20
            self.speed = -5
            index = randint(6, 9)
        else:
            index = 0
        self.image = Game.Sprite_container.get_sprites("rocks")[index]
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self._angle = randint(0, 360)
        angle = radians(self._angle)
        self.speed_x = self.speed * sin(angle)
        self.speed_y = self.speed * cos(angle)
        self.newpos()

        self.dirty = 1

    def newpos(self) -> None:
        """Defines a new ramdom position"""
        self.rect.left = randint(self.rect.width + 5, Settings.playground.width - self.rect.width - 5)
        self.rect.top = randint(self.rect.height + 5, Settings.playground.height - self.rect.height - 5)
        self.dirty = 1

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Main update function of the sprite.

        The method controls which behaviour of the sprite changes:

        Args:
            actiobn (str): 
             # "go": computes the new position
             # "newpos": defines a new randomly choosen position 
        """
        if "action" in kwargs.keys():
            if kwargs["action"] == "go":
                self.rect.move_ip(self.speed_x, self.speed_y)
                if self.rect.right < 0:
                    self.rect.left = Settings.playground.width
                if self.rect.left > Settings.playground.width:
                    self.rect.right = 0
                if self.rect.bottom < 0:
                    self.rect.top = Settings.playground.height
                if self.rect.top > Settings.playground.height:
                    self.rect.bottom = 0
                self.dirty = 1
            if kwargs["action"] == "newpos":
                self.newpos()


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
        self._background = Background("background_blue.png")
        self._ship = pygame.sprite.LayeredDirty(Ship())
        self._all_rocks = pygame.sprite.LayeredDirty()
        self._bullets = pygame.sprite.LayeredDirty()
        self._timer_rock = Timer(Settings.rock_intervall, True)
        self._running = True

        self._ship.clear(self._screen, self._background.image)
        self._all_rocks.clear(self._screen, self._background.image)
        self._bullets.clear(self._screen, self._background.image)

    def watch_for_events(self) -> None:
        """Looking for any type of event and poke a reaction."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self._running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self._running = False
                elif event.key == K_UP:
                    self._ship.sprites()[0].update(mode=1)
                elif event.key == K_LEFT:
                    self._ship.sprites()[0].update(direction=1)
                elif event.key == K_RIGHT:
                    self._ship.sprites()[0].update(direction=-1)
                elif event.key == K_KP_ENTER:
                    self._ship.sprites()[0].update(shoot=True)
                elif event.key == K_RETURN:
                    self._ship.sprites()[0].update(shoot=True)
            elif event.type == KEYUP:
                if event.key == K_UP:
                    self._ship.sprites()[0].update(mode=0)

    def draw(self) -> None:
        """Draws all sprite on the screen."""
        self._background.draw(self._screen)
        ship_rects = self._ship.draw(self._screen)
        rock_rects = self._all_rocks.draw(self._screen)
        bullet_rects = self._bullets.draw(self._screen)

        rects = ship_rects + rock_rects + bullet_rects

        pygame.display.update(rects)

    def update(self) -> None:
        """This method is responsible for the main game logic."""
        if self._timer_rock.is_next_stop_reached():
            if len(self._all_rocks) < Settings.max_big_rocks:
                rock = Rock("big")
                while pygame.sprite.collide_rect(rock, self._ship.sprites()[0]):
                    rock.update(action="newpos")
                self._all_rocks.add(rock)
        if self._running:
            self._ship.sprites()[0].update(go=True)
            self._all_rocks.update(action="go")
            self._bullets.update()

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