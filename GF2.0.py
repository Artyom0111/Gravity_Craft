import csv
import os
import random

# import the pygame module
import pygame

# will make it easier to use pygame functions
from pygame.math import Vector2

# initializes the pygame module
pygame.init()

# creates a screen variable of size 800 x 600
screen = pygame.display.set_mode([900, 700])

# controls the main game while loop
done = False

# controls whether or not to start the game from the main menu
start = False

# sets the frame rate of the program
clock = pygame.time.Clock()

"""
CONSTANTS
"""
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

"""lambda functions are anonymous functions that you can assign to a variable.
e.g.
1. x = lambda x: x + 2  # takes a parameter x and adds 2 to it
2. print(x(4))
>>6
"""
color = lambda: tuple([random.randint(0, 255) for i in range(3)])  # lambda function for random color, not a constant.
GRAVITY = Vector2(0, 1.52)  # Vector2 is a pygame

"""
Main player class
"""

class Player(pygame.sprite.Sprite):
    """Class for player. Holds update method, win and die variables, collisions and more."""
    win: bool
    died: bool

    def __init__(self, image, platforms, pos, *groups):
        """
        :param image: block face avatar
        :param platforms: obstacles such as coins, blocks, spikes, and orbs
        :param pos: starting position
        :param groups: takes any number of sprite groups.
        """
        super().__init__(*groups)
        self.onGround = False  # player on ground?
        self.platforms = platforms  # obstacles but create a class variable for it
        self.died = False  # player died?
        self.win = False  # player beat level?

        self.image = pygame.transform.smoothscale(image, (40, 40))
        self.rect = self.image.get_rect(center=pos)  # get rect gets a Rect object from the image
        self.jump_amount = 12  # jump strength
        self.particles = []  # player trail
        self.isjump = False  # is the player jumping?
        self.vel = Vector2(0, 0)  # velocity starts at zero

    def collide(self, yvel, platforms):

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                """pygame sprite builtin collision method,
                sees if player is colliding with any obstacles"""
                if isinstance(p, Orb) and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
                    pygame.draw.circle(alpha_surf, (255, 255, 0), p.rect.center, 18)
                    screen.blit(pygame.image.load("images/editor-0.9s-47px.gif"), p.rect.center)
                    self.jump_amount = 14  # gives a little boost when hit orb
                    self.jump()
                    self.jump_amount = 12  # return jump_amount to normal

                if isinstance(p, End):
                    self.win = True

                if isinstance(p, Spike):
                    self.died = True  # die on spike


                if isinstance(p, Platform):  # these are the blocks (may be confusing due to self.platforms)

                    if yvel > 0:
                        """if player is going down(yvel is +)"""
                        self.rect.bottom = p.rect.top  # dont let the player go through the ground
                        self.vel.y = 0  # rest y velocity because player is on ground

                        # set self.onGround to true because player collided with the ground
                        self.onGround = True

                        # reset jump
                        self.isjump = False
                    elif yvel < 0:
                        """if yvel is (-),player collided while jumping"""
                        self.rect.top = p.rect.bottom  # player top is set the bottom of block like it hits it head
                    else:
                        """otherwise, if player collides with a block, he/she dies."""
                        self.vel.x = 0
                        self.rect.right = p.rect.left  # dont let player go through walls
                        self.died = True

    def jump(self):
        self.vel.y = -self.jump_amount  # players vertical velocity is negative so ^

    def update(self):
        """update player"""
        if self.isjump:
            if self.onGround:
                """if player wants to jump and player is on the ground: only then is jump allowed"""
                self.jump()

        if not self.onGround:  # only accelerate with gravity if in the air
            self.vel += GRAVITY  # Gravity falls

            # max falling speed
            if self.vel.y > 100: self.vel.y = 100

        # do x-axis collisions
        self.collide(0, self.platforms)

        # increment in y direction
        self.rect.top += self.vel.y

        # assuming player in the air, and if not it will be set to inversed after collide
        self.onGround = False

        # do y-axis collisions
        self.collide(self.vel.y, self.platforms)

        # check if we won or if player won
        eval_outcome(self.win, self.died)

"""
Obstacle classes
"""

# Parent class
class Draw(pygame.sprite.Sprite):
    """parent class to all obstacle classes; Sprite class"""

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

#  ====================================================================================================================#
#  classes of all obstacles. this may seem repetitive but it is useful(to my knowledge)
#  ====================================================================================================================#
# children
class Platform(Draw):
    """block"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

class Spike(Draw):
    """spike"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

class Orb(Draw):
    """orb. click space or up arrow while on it to jump in midair"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

class End(Draw):
    "place this at the end of the level"

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

"""
Functions
"""

def init_level(map):
    """this is similar to 2d lists. it goes through a list of lists, and creates instances of certain obstacles
    depending on the item in the list"""
    x = 0
    y = 0

    for row in map:
        for col in row:

            if col == "0":
                Platform(block, (x, y), elements)

            if col == "Spike":
                Spike(spike, (x, y), elements)

            if col == "Orb":
                orbs.append([x, y])
                Orb(orb, (x, y), elements)

            if col == "End":
                End(avatar, (x, y), elements)
            x += 40
        y += 40
        x = 0

def blitRotate(surf, image, pos, originpos: tuple):
    """
    rotate the player
    :param surf: Surface
    :param image: image to rotate
    :param pos: position of image
    :param originpos: x, y of the origin to rotate about
    """
    # calcaulate the axis aligned bounding box of the rotated image
    w, h = image.get_size()
    box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(0) for p in box]

    # make sure the player does not overlap, uses a few lambda functions(new things that we did not learn about number1)
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
    # calculate the translation of the pivot
    pivot = Vector2(originpos[0], -originpos[1])
    pivot_rotate = pivot.rotate(0)
    pivot_move = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (pos[0] - originpos[0] + min_box[0] - pivot_move[0], pos[1] - originpos[1] - max_box[1] + pivot_move[1])

    # get a rotated image
    rotated_image = pygame.transform.rotozoom(image, 0, 1)

    # rotate and blit the image
    surf.blit(rotated_image, origin)

def won_screen():
    """show this screen when beating a level"""
    global level, fill
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("yellow"))

    w1 = font.render('👾 Good Game 👾', True, BLUE)


    screen.blit(w1, (350, 350))

    wait_for_key()
    reset()

def death_screen():
    """show this screenon death"""
    global  fill
    fill = 0
    player_sprite.clear(player.image, screen)
    game_over = font.render("👾 You lose. One more? 👾", True, WHITE)

    screen.fill(pygame.Color("sienna"))
    screen.blits([[game_over, (290, 300)], [tip, (100, 500)]])

    wait_for_key()
    reset()

def eval_outcome(won: bool, died: bool):
    """simple function to run the win or die screen after checking won or died"""
    if won:
        won_screen()
    if died:
        death_screen()

def block_map(level_num):
    """
    :type level_num: rect(screen, BLACK, (0, 0, 32, 32))
    open a csv file that contains the right level map
    """
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl

def start_screen():
    """main menu. option to switch level, and controls guide, and game overview."""
    global level
    if not start:
        screen.fill(BLACK)
        if pygame.key.get_pressed()[pygame.K_1]:
            level = 0

        welcome = font.render(f"Welcome to Gravity Craft. Choose Beta Version by keypad", True, WHITE)

        controls = font.render("Controls: jump: Space/Up", True, BLUE)

        escape = font.render("exit: Esc", True, RED)

        screen.blits([[welcome, (100, 100)], [controls, (100, 200)], [tip, (100, 500)], [escape, (100, 300)]])

def reset():
    """resets the sprite groups, music, etc. for death and new level"""
    global player, elements, player_sprite, level

    if level == 0:
        pygame.mixer.music.load(os.path.join("music", "GigaChad_Theme_74842929.mp3"))
    pygame.mixer_music.play()
    player_sprite = pygame.sprite.Group()
    elements = pygame.sprite.Group()
    player = Player(avatar, elements, (100, 150), player_sprite)
    init_level(
            block_map("level_1.csv"))

def move_map():
    """moves obstacles along the screen"""
    for sprite in elements:
        sprite.rect.x -= CameraX

def wait_for_key():
    """separate game loop for waiting for a key press while still running game loop
    """
    global level, start
    waiting = True
    while waiting:
        clock.tick(60)
        pygame.display.flip()

        if not start:
            start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

def resize(img, size=(40, 40)):
    """resize images
    :param img: image to resize
    :type img: im not sure, probably an object
    :param size: default is 32 because that is the tile size
    :type size: tuple
    :return: resized img
    :rtype:object?
    """
    resized = pygame.transform.smoothscale(img, size)
    return resized

"""
Global variables
"""
font = pygame.font.SysFont("lucidaconsole", 20)

# square block face is main character the icon of the window is the block face
avatar = pygame.image.load(os.path.join("images", "sticker.webp"))  # load the main character
pygame.display.set_icon(avatar)
#  this surface has an alpha value with the colors, so the player trail will fade away using opacity
alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

# sprite groups
player_sprite = pygame.sprite.Group()
elements = pygame.sprite.Group()

# images
spike = pygame.image.load(os.path.join("images", "ugol.webp"))
spike = resize(spike)
block = pygame.image.load(os.path.join("images", "Lava.jpg"))
block = pygame.transform.smoothscale(block, (40, 40))
orb = pygame.image.load((os.path.join("images", "star.webp")))
orb = pygame.transform.smoothscale(orb, (40, 40))

#  ints
fill = 0
CameraX = 0
level = 0

# list
particles = []
orbs = []
win_cubes = []

# set window title suitable for game
pygame.display.set_caption('Gravity Craft')

# initialize the font variable to draw text later
text = font.render('image', False, (255, 255, 0))

# music
music = pygame.mixer_music.load(os.path.join("music", "Yendorami — Gravity Falls (Opening Theme) (www.lightaudio.ru).mp3"))
pygame.mixer_music.play()

# bg image
bg = pygame.image.load(os.path.join("images", "Ustena2.0.png"))

# show tip on start and on death
tip = font.render("tip: tap and hold for the first few seconds of the level", True, GREEN)

while not done:
    keys = pygame.key.get_pressed()

    if not start:
        wait_for_key()
        reset()

        start = True

    player.vel.x = 10

    eval_outcome(player.win, player.died)
    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
        player.isjump = True

    # Reduce the alpha of all pixels on this surface each frame.
    # Control the fade2 speed with the alpha value.

    alpha_surf.fill((255, 255, 255, 1), special_flags=pygame.BLEND_RGBA_MULT)

    player_sprite.update()
    CameraX = player.vel.x  # for moving obstacles
    move_map()  # apply CameraX to all elements

    screen.blit(bg, (0, 0))  # Clear the screen(with the bg)

    if player.isjump:
        """rotate the player by an angle and blit it if player is jumping"""
        blitRotate(screen, player.image, player.rect.center, (20, 20))
    else:
        """if player.isjump is false, then just blit it normally(by using Group().draw() for sprites"""
        player_sprite.draw(screen)  # draw player sprite group
    elements.draw(screen)  # draw all other obstacles

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                """User friendly exit"""
                done = True
            if event.key == pygame.K_2:
                """change level by keypad"""
                player.jump_amount += 1

            if event.key == pygame.K_1:
                """change level by keypad"""

                player.jump_amount -= 1

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
