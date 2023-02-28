import pygame
from pygame.locals import *
from pygame.math import Vector2 as v2
import random, sys

reward = 0;

class Paddle(pygame.sprite.Sprite):
    def __init__(self, width, height, speed, center, color, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height)).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = speed
        self.vx = 0
        self.bounds = screen.get_rect()

    def move_left(self):
        self.vx = -self.speed

    def move_right(self):
        self.vx = self.speed

    def stop_left(self):
        if self.vx == -self.speed:
            self.vx = 0

    def stop_right(self):
        if self.vx == self.speed:
            self.vx = 0

    def update(self):
        self.rect.move_ip(self.vx, 0)
        if not self.bounds.contains(self.rect):
            self.vx = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, velocity, center, paddle, blocks, color, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius * 2, radius * 2)).convert()
        self.image.fill("white")
        self.image.set_colorkey("white")
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.v = v2(velocity)
        self.bounds = screen.get_rect()
        self.paddle = paddle
        self.blocks = blocks
        self.screen = screen

    def update(self):
        if pygame.time.get_ticks() < 3000:
            return

        self.rect.move_ip(self.v.x, 0)
        if not self.bounds.contains(self.rect) or pygame.sprite.spritecollide(self, self.blocks, True):
            self.v.x = -self.v.x
            self.rect.move_ip(self.v.x, 0)

        self.rect.move_ip(0, self.v.y)
        if not self.bounds.contains(self.rect) or pygame.sprite.spritecollide(self, self.blocks, True):
            if self.rect.bottom > self.bounds.bottom:
                write_and_quit(self.screen, "You Lost! :(")
                reward = -1
            self.v.y = -self.v.y
            self.rect.move_ip(0, self.v.y)

        if pygame.sprite.collide_rect(self, self.paddle):
            self.v.from_polar((self.v.magnitude(), -90 + 120 * (self.rect.centerx - self.paddle.rect.centerx) / self.paddle.rect.width))

class Block(pygame.sprite.Sprite):
    def __init__(self, rect, color):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.image = pygame.Surface(rect.size).convert()
        self.image.fill(color)

def write_and_quit(screen, message):
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, "black")
    textpos = text.get_rect(centerx=screen.get_width() // 2, centery=screen.get_height() // 2)
    screen.blit(text, textpos)
    pygame.display.update(textpos)
    pygame.time.wait(3000)
    sys.exit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Breakout")
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill("white")

    screen.blit(background, (0, 0))
    pygame.display.flip()

    paddle = Paddle(50, 10, 5, (screen.get_width() // 2, screen.get_height() - 20), "blue", screen)

    block_width = 30
    block_height = 10
    block_padding = 5
    block_top_offset = 60
    colors = ("red", "orange", "green", "yellow")
    n_rows = len(colors) * 2
    blocks = pygame.sprite.RenderPlain(
        Block(
            Rect(left, top, block_width, block_height),
            colors[int(len(colors) * (top - (block_padding + block_top_offset)) / ((block_height + block_padding) * n_rows))],
        )
        for left in range(block_padding, screen.get_width() - block_width, block_width + block_padding)
        for top in range(block_padding + block_top_offset, (block_height + block_padding) * n_rows + block_padding + block_top_offset, block_height + block_padding)
    )

    ball = Ball(4, (5, 5), (30 + random.randrange(0, screen.get_width() - 60), screen.get_height() // 2), paddle, blocks, "black", screen)

    allsprites = pygame.sprite.RenderUpdates((paddle, ball, *blocks))

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    paddle.move_left()
                elif event.key == K_RIGHT:
                    paddle.move_right()
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    paddle.stop_left()
                elif event.key == K_RIGHT:
                    paddle.stop_right()

        pygame.event.pump()

        allsprites.clear(screen, background)
        allsprites.update()
        pygame.display.update(allsprites.draw(screen))

        if len(blocks) == 0:
            write_and_quit(screen, "You Won! :)")

        clock.tick(60)

if __name__ == "__main__":
    main()
