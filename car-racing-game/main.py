import os
import time
import math
import pygame

from pygame import image
from pygame.version import PygameVersion, ver
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("images/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("images/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("images/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("images/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption ("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
LEVEL_SPEED = 0.2
PATH = [
    (166, 102), (68, 92), (59, 454), (288, 717), (403, 700), (426, 509), (568, 502), (606, 690), (724, 722), (736, 410), (505, 368), (395, 315), (492, 259), (721, 255), (729, 96), (315, 73), (275, 384), (176, 388), (159, 257)
]

class GameInfo(object):
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        
        return round(time.time() - self.level_start_time)

class AbstractCar:
    IMAGE = RED_CAR
    def __init__(self, max_vel, rotation_vel):
        self.image = self.IMAGE
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POSITION
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.image, (self.x, self.y), self.angle)

    def move_foward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.x -= horizontal
        self.y -= vertical

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POSITION
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMAGE = RED_CAR
    START_POSITION = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class ComputerCar(AbstractCar):
    IMAGE = GREEN_CAR
    START_POSITION = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)
    
    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2 # to avoid div by 0
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        different_in_angle = self.angle - math.degrees(desired_radian_angle)

        if different_in_angle >= 180:
            different_in_angle -= 360
        
        if different_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(different_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(different_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level-1) * LEVEL_SPEED
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_infos):
    for image , pos in images:
        win.blit(image, pos)

    level_text = MAIN_FONT.render(f"Level {game_infos.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70 ))

    time_text = MAIN_FONT.render(f"Time {game_infos.get_level_time()}", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40 ))

    velocity_text = MAIN_FONT.render(f"Vel {round(player_car.vel, 1)} px/s", 1, (255, 255, 255))
    win.blit(velocity_text, (10, HEIGHT - velocity_text.get_height() - 10 ))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        moved = True
        player_car.move_foward()
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()
    
    if not moved:
        player_car.reduce_speed()


def handel_collison(player_car, computer_car, game_infos):
    if player_car.collide(TRACK_BORDER_MASK) is not None:
        player_car.bounce()
    
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide is not None:
        game_infos.next_level()
        blit_text_center(WIN, MAIN_FONT, "You lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        #game_infos.reset()
        player_car.reset()
        computer_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide is not None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_infos.next_level()
            player_car.reset()
            computer_car.next_level(game_infos.level)


run = True
clock = pygame.time.Clock()
images = [
    (GRASS, (0, 0)),
    (TRACK, (0, 0)),
    (FINISH, FINISH_POSITION),
    (TRACK_BORDER, (0, 0))
]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 4, PATH)
game_infos = GameInfo()

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, game_infos)

    pygame.display.update()

    while not game_infos.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start the level {game_infos.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_infos.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    computer_car.path.append(pygame.mouse.get_pos())
    
    move_player(player_car)
    computer_car.move()

    handel_collison(player_car, computer_car, game_infos)

    if game_infos.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_infos.reset()
        player_car.reset()
        computer_car.reset()


#print(computer_car.path)
pygame.quit()
