import pygame
import unittest


class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 50, 50)
        self.jump_height = 10
        self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.rect.y -= self.jump_height

    def fall(self):
        if self.is_jumping:
            self.rect.y += self.jump_height
            self.is_jumping = False

class Platform:
    def __init__(self):
        self.rect = pygame.Rect(0, 300, 800, 20)

    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)

class Spike:
    def __init__(self):
        self.rect = pygame.Rect(400, 280, 20, 20)

class EndPoint:
    def __init__(self):
        self.rect = pygame.Rect(750, 250, 20, 50)

class Background:
    def __init__(self):
        self.image = None  # Замените на вашу текстуру фона

    def load_image(self, image_path):
        self.image = pygame.image.load(image_path)

class TestGameObjects(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.player = Player()
        self.platform = Platform()
        self.spike = Spike()
        self.end_point = EndPoint()
        self.background = Background()

    def test_player_exists(self):
        self.assertIsNotNone(self.player)
        self.assertIsInstance(self.player.rect, pygame.Rect)

    def test_player_jump(self):
        self.player.jump()
        self.assertEqual(self.player.rect.y, 40)
        self.assertTrue(self.player.is_jumping)

    def test_player_fall(self):
        self.player.jump()
        self.player.fall()
        self.assertEqual(self.player.rect.y, 50)
        self.assertFalse(self.player.is_jumping)

    def test_platform_exists(self):
        self.assertIsNotNone(self.platform)
        self.assertIsInstance(self.platform.rect, pygame.Rect)

    def test_platform_collision(self):
        self.player.rect.y = 300
        self.assertTrue(self.platform.is_colliding(self.player))

    def test_spike_exists(self):
        self.assertIsNotNone(self.spike)
        self.assertIsInstance(self.spike.rect, pygame.Rect)

    def test_end_point_exists(self):
        self.assertIsNotNone(self.end_point)
        self.assertIsInstance(self.end_point.rect, pygame.Rect)

    def test_background_exists(self):
        self.assertIsNotNone(self.background)

    def test_background_load_image(self):
        self.background.load_image("assets/images/Ustena2.0.png")
        self.assertIsNotNone(self.background.image)  # Проверка, что изображение загружено

    def tearDown(self):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
