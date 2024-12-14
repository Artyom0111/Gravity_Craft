import csv
import os
import pygame
from pygame.math import Vector2

pygame.init()
screen = pygame.display.set_mode([900, 700])
done = False
start = False
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

GRAVITY = Vector2(0, 1.52)


class Player(pygame.sprite.Sprite):
    """Класс игрока.

    Этот класс управляет поведением игрока, включая прыжки, столкновения с платформами и
    взаимодействие с игровыми объектами, такими как орбы и шипы.

    Атрибуты:
        onGround (bool): Указывает, находится ли игрок на земле.
        platforms (pygame.sprite.Group): Группа платформ, с которыми игрок может столкнуться.
        died (bool): Указывает, погиб ли игрок.
        win (bool): Указывает, выиграл ли игрок.
        image (pygame.Surface): Изображение игрока.
        rect (pygame.Rect): Прямоугольник, представляющий положение и размер игрока.
        jump_amount (int): Сила прыжка игрока.
        isjump (bool): Указывает, выполняет ли игрок прыжок.
        vel (Vector2): Вектор скорости игрока.
    """

    def __init__(self, image, platforms, pos, *groups):
        super().__init__(*groups)
        self.onGround = False
        self.platforms = platforms
        self.died = False
        self.win = False
        self.image = pygame.transform.smoothscale(image, (40, 40))
        self.rect = self.image.get_rect(center=pos)
        self.jump_amount = 13
        self.isjump = False
        self.vel = Vector2(0, 0)

    def collide(self, yvel, platforms):
        """Обработка столкновений игрока с платформами.

        Этот метод проверяет столкновения игрока с платформами и обрабатывает
        различные взаимодействия, такие как прыжки, победа или смерть.

        Параметры:
            yvel (float): Вертикальная скорость игрока.
            platforms (pygame.sprite.Group): Группа платформ для проверки столкновений.
        """
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, Orb) and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
                    pygame.draw.circle(alpha_surf, (255, 255, 0), p.rect.center, 18)
                    screen.blit(pygame.image.load("assets/images/editor-0.9s-47px.gif"), p.rect.center)
                    self.jump_amount = 15.2
                    self.jump()
                    self.jump_amount = 13

                if isinstance(p, End):
                    self.win = True

                if isinstance(p, Spike):
                    self.died = True

                if isinstance(p, Platform):
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.vel.y = 0
                        self.onGround = True
                        self.isjump = False
                    elif yvel < 0:
                        self.rect.top = p.rect.bottom
                    else:
                        self.vel.x = 0
                        self.rect.right = p.rect.left
                        self.died = True

    def jump(self):
        """Метод прыжка.

        Этот метод устанавливает вертикальную скорость игрока, чтобы он мог прыгнуть.
        """
        self.vel.y = -self.jump_amount

    def update(self):
        """Обновление состояния игрока.

        Этот метод обновляет положение игрока, проверяет столкновения и управляет прыжками.
        """
        if self.isjump and self.onGround:
            self.jump()

        if not self.onGround:
            self.vel += GRAVITY
            if self.vel.y > 100:
                self.vel.y = 100

        self.collide(0, self.platforms)
        self.rect.top += self.vel.y
        self.onGround = False
        self.collide(self.vel.y, self.platforms)

        # Оценка результата игры
        eval_outcome(self.win, self.died)


class Draw(pygame.sprite.Sprite):
    """Базовый класс для объектов, которые нужно рисовать.

    Этот класс предоставляет базовые функции для всех объектов, которые будут отображаться на экране.

    Атрибуты:
        image (pygame.Surface): Изображение объекта.
        rect (pygame.Rect): Прямоугольник, представляющий положение и размер объекта.
    """

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


class Platform(Draw):
    """Класс платформы.

    Этот класс представляет платформу, на которой может стоять игрок.
    """

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    """Класс шипа.

    Этот класс представляет шипы, которые убивают игроку при столкновении.
    """

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Orb(Draw):
    """Класс орбиты.

    Этот класс представляет орбы, которые игрок может использовать для двойного прыжка.
    """

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

class End(Draw):
    """Класс конечной точки.

    Этот класс представляет конечную точку уровня, в которую игрок должен попасть для завершения уровня.
    """

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


def init_level(map):
    """Инициализация уровня из карты.

    Этот метод создает объекты уровня на основе данных, полученных из CSV-файла.
    Он обрабатывает каждый элемент карты и создает соответствующие объекты.

    Параметры:
        map (list): Список строк, представляющих уровень.
    """
    x, y = 0, 0
    for row in map:
        for col in row:
            if col == "00":
                Platform(block, (x, y), elements)
            if col == "Sp":
                Spike(spike, (x, y), elements)
            if col == "Or":
                orbs.append([x, y])
                Orb(orb, (x, y), elements)
            if col == "End":
                End(avatar, (x, y), elements)
            x += 40
        y += 40
        x = 0


def blitRotate(surf, image, pos, originpos):
    """Функция для вращения изображения.

    Эта функция поворачивает изображение относительно заданной точки и отображает его на поверхности.

    Параметры:
        surf (pygame.Surface): Поверхность, на которую будет нанесено изображение.
        image (pygame.Surface): Изображение, которое будет вращаться.
        pos (tuple): Позиция, где будет размещено изображение.
        originpos (tuple): Позиция, относительно которой будет происходить вращение.
    """
    w, h = image.get_size()
    box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(0) for p in box]
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
    pivot = Vector2(originpos[0], -originpos[1])
    pivot_rotate = pivot.rotate(0)
    pivot_move = pivot_rotate - pivot
    origin = (pos[0] - originpos[0] + min_box[0] - pivot_move[0],
              pos[1] - originpos[1] - max_box[1] + pivot_move[1])
    rotated_image = pygame.transform.rotozoom(image, 0, 1)
    surf.blit(rotated_image, origin)


def won_screen():
    """Экран победы.

    Этот метод отображает экран победы, когда игрок завершает уровень.
    Он показывает сообщение о победе и ожидает нажатия клавиши для продолжения.
    """
    global level, fill
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("yellow"))
    w1 = font.render('👾 Good Game 👾', True, BLUE)
    screen.blit(w1, (350, 350))
    wait_for_key()  # Ожидание нажатия клавиши
    reset()  # Сброс состояния игры


def death_screen():
    """Экран смерти.

    Этот метод отображает экран смерти, когда игрок сталкивается со шипом.
    Он показывает сообщение о проигрыше и ожидает нажатия клавиши для продолжения.
    """
    global fill
    fill = 0
    player_sprite.clear(player.image, screen)
    game_over = font.render("👾 You lose. One more? 👾", True, WHITE)
    screen.fill(pygame.Color("sienna"))
    screen.blits([[game_over, (290, 300)], [tip, (100, 500)]])
    wait_for_key()
    reset()


def eval_outcome(won, died):
    """Оценка результата игры.

    Этот метод проверяет, выиграл ли игрок или погиб, и вызывает соответствующий экран.

    Параметры:
        won (bool): Указывает, выиграл ли игрок.
        died (bool): Указывает, умер ли игрок.
    """
    if won:
        won_screen()
    if died:
        death_screen()


def block_map(level_num):
    """Загрузка карты уровня из CSV-файла.

    Этот метод считывает данные уровня из CSV-файла и возвращает их в виде двумерного списка.

    Параметры:
        level_num (str): Имя файла, содержащего карту уровня.

    Возвращает:
        list: Двумерный список, представляющий уровень.
    """
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl


def start_screen():
    """Экран выбора уровня.

    Этот метод отображает экран, на котором игрок может выбрать уровень.
    Он показывает инструкции и ожидает нажатия клавиши для начала игры.
    """
    global level
    if not start:
        screen.fill(BLACK)
        if pygame.key.get_pressed()[pygame.K_1]:
            level = 0  # Установка уровня 0 при нажатии клавиши 1
        welcome = font.render(f"Welcome to Gravity Craft. Choose Beta Version by keypad", True, WHITE)
        controls = font.render("Controls: jump: Space/Up", True, BLUE)
        escape = font.render("Exit: Esc", True, RED)
        screen.blits([[welcome, (100, 100)], [controls, (100, 200)], [tip, (100, 500)], [escape, (100, 300)]])


def reset():
    """Сброс состояния игры.

    Этот метод сбрасывает игру и инициализирует все необходимые объекты,
    такие как игрок и уровень, загружая данные из CSV-файла.
    """
    global player, elements, player_sprite, level
    if level == 0:
        pygame.mixer.music.load(os.path.join("assets/music", "GigaChad_Theme_74842929.mp3"))
    pygame.mixer.music.play()  # Воспроизведение музыки
    player_sprite = pygame.sprite.Group()
    elements = pygame.sprite.Group()
    player = Player(avatar, elements, (100, 140), player_sprite)
    init_level(block_map("level_1.csv"))


def move_map():
    """Движение карты в зависимости от игрока.

    Этот метод перемещает карту в зависимости от положения игрока,
    чтобы создать эффект прокрутки.
    """
    for sprite in elements:
        sprite.rect.x -= CameraX


def wait_for_key():
    """Ожидание нажатия клавиши.

    Этот метод ожидает, пока игрок не нажмет клавишу, чтобы продолжить игру.
    Он также обрабатывает события выхода из игры.
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
    """Изменение размера изображения.

    Этот метод изменяет размер изображения до заданных параметров.

    Параметры:
        img (pygame.Surface): Изображение, которое нужно изменить.
        size (tuple): Новый размер изображения.

    Возвращает:
        pygame.Surface: Измененное изображение.
    """
    return pygame.transform.smoothscale(img, size)


font = pygame.font.SysFont("lucidaconsole", 20)
avatar = pygame.image.load(os.path.join("assets/images", "sticker.webp"))
pygame.display.set_icon(avatar)
alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
player_sprite = pygame.sprite.Group()
elements = pygame.sprite.Group()
spike = pygame.image.load(os.path.join("assets/images", "ugol.webp"))
spike = resize(spike)
block = pygame.image.load(os.path.join("assets/images", "Lava.jpg"))
block = pygame.transform.smoothscale(block, (40, 40))
orb = pygame.image.load(os.path.join("assets/images", "star.webp"))
orb = pygame.transform.smoothscale(orb, (40, 40))
CameraX = 0
level = 0
orbs = []

pygame.display.set_caption('Gravity Craft')
music = pygame.mixer.music.load(os.path.join("assets/music", "Yendorami — Gravity Falls (Opening Theme) (www.lightaudio.ru).mp3"))
pygame.mixer.music.play()
bg = pygame.image.load(os.path.join("assets/images", "Ustena2.0.png"))
tip = font.render("tip: Press 'Esc', don`t waste your time!", True, GREEN)

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

    alpha_surf.fill((255, 255, 255, 1), special_flags=pygame.BLEND_RGBA_MULT)
    player_sprite.update()
    CameraX = player.vel.x
    move_map()
    screen.blit(bg, (0, 0))

    if player.isjump:
        blitRotate(screen, player.image, player.rect.center, (20, 20))
    else:
        player_sprite.draw(screen)
    elements.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            if event.key == pygame.K_2:
                player.jump_amount += 1
            if event.key == pygame.K_1:
                player.jump_amount -= 1

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
