import pygame
import sys
from math import sin, cos, radians
from random import randint, choice


# Дерево Пифагора
def ftree(pos, length, angle, turn_angle, depth, color, split):
    if depth == 0:
        return
    x, y = pos
    new_x = x + cos(radians(angle)) * length
    new_y = y - sin(radians(angle)) * length
    pygame.draw.line(screen, color, pos, (int(new_x), int(new_y)))

    new_pos = (new_x, new_y)
    length = 0.69 * length
    color1 = color2 = color
    if split:
        color1 = BLUE
        color2 = RED
    ftree(new_pos, length, (angle + turn_angle), turn_angle, depth - 1, color1, False)
    ftree(new_pos, length, (angle - turn_angle), turn_angle, depth - 1, color2, False)


# Класс персонажа, загрузка изображений, работа анимаций, а также обработка нажатий клавиш
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()
        self.player_duck = pygame.image.load('graphics/p1_duck.png').convert_alpha()
        self.player_duck_rect = self.player_duck.get_rect(midbottom=(80, 300))
        self.player_slide_fl = 5
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.15)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()
        if keys[pygame.K_DOWN] and self.rect.bottom < 300:
            self.gravity = 14
        if keys[pygame.K_DOWN] and self.rect.bottom == 300:
            self.player_slide_fl = 1

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump

        elif self.player_slide_fl > 0:
            self.image = self.player_duck
            self.rect = self.image.get_rect(midbottom=(80, 300))
            self.player_slide_fl -= 1
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
            self.rect = self.image.get_rect(midbottom=(80, 300))

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation()


# Класс препятствий, загрузка изображений, определение типа препятствий - муха или улитка
# анимация их движения
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'fly':
            fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = choice([225, 205, 270])
        else:
            snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()

        # self.move(self.rect.x, game_active, game_speed)
        self.rect.x -= 6 + game_speed
        self.destroy()

    def destroy(self):
        global fl
        if self.rect.x <= -100:
            fl = 1

            # sc(ill, 1)
            self.kill()


# Функция вывода счета игрока
def display_score():
    global current_time
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time


# Функция проверки на коллизию
def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        # sc(ill, 0)
        obstacle_group.empty()
        return False
    else:
        return True


# Объявление начальных значений переменных, цветов, условия игры - game_active,
# загрузка музыки и тд.
BLACK = (111, 196, 169)
WHITE = (0, 0, 0)
BLUE = (111, 196, 169)
RED = (111, 196, 169)
turn_angle = 0
INIT_POS = (200, 250)
INIT_POS2 = (600, 250)
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Runner")
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0
bg_Music = pygame.mixer.Sound('audio/music.wav')
bg_Music.set_volume(0.1)
bg_Music.play(loops=-1)

player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

# Intro screen, все что есть на начальном экране, загрузка шрифтов и самого текста
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

# текстуры неба и земли
sky_surf = pygame.image.load('graphics/Sky.png').convert_alpha()
ground_surf = pygame.image.load('graphics/ground.png').convert_alpha()

game_name = test_font.render('Pixel Runner', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))

game_message = test_font.render('Press space to run', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(400, 330))

# скорость игры
game_speed = 0
fl_r = 0

# Timer, таймеры, через какое время появляется препятствие
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

game_speed_timer = pygame.USEREVENT + 2
pygame.time.set_timer(game_speed_timer, 5000)

# Основной цикл игры, обработка всех событий
while True:
    for event in pygame.event.get():
        # Завершение игры по кнопке крестик в окне
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            # Создание препятствия по таймеру
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
                pygame.time.set_timer(obstacle_timer,
                                      max(int(1500 - game_speed * 100 * (1 + randint(0, 10) * 0.1)), 100))

            # Увеличение скорости игры по таймеру
            if event.type == game_speed_timer:
                game_speed += 1
                print(game_speed)

        else:
            # Когда игра закончена, по нажатию пробела игра начинается снова
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

    if game_active:
        fl_r = 0
        turn_angle = 0
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))
        score = display_score()

        # Player
        # Рисует персонажа
        player.draw(screen)
        player.update()
        # Рисует препятствие
        obstacle_group.draw(screen)
        obstacle_group.update()
        # collision
        # проверяет на коллизию, если она существует игра заканчивается
        game_active = collision_sprite()
    else:
        # Если игра окончена, то появляется экран с очками игрока
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 330))
        screen.blit(game_name, game_name_rect)

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)
        # Скорость игры сбрасывается к начальному уровню
        game_speed = 0
        pygame.time.set_timer(obstacle_timer, 1500)
        # Если была нажата кнопка 'R' то начинается рекурсия, дерево Пифагора появляется на экране
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            fl_r = 1
            print('key')
        # Сам процесс изображения дерева Пифагора начинается тут
        if fl_r:
            ftree(INIT_POS, 50, 90, turn_angle, 9, WHITE, True)
            ftree(INIT_POS2, 50, 90, turn_angle, 9, WHITE, True)
            # turn_angle += 0.1
            if turn_angle < 40:
                turn_angle += 0.1
    # Обновление экрана и ограничивание максимальной частоты кадров
    pygame.display.update()
    clock.tick(60)
