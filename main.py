import pygame

pygame.init()

BLACK = (0, 0, 0)
WHITE = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

WIDTH, HEIGHT = 625, 850
TOP_BLACK_SPACE = 50
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT + TOP_BLACK_SPACE))
pygame.display.set_caption("Breakout Game")

FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 65, 15
BALL_RADIUS = 8

FONT = pygame.font.Font(None, 60)
WINNING_SCORE = 336
restart = False

volume = 0.3


class Paddle:
    COLOR = WHITE
    VEL = 5

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.x -= self.VEL
        else:
            self.x += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = 3
        self.y_vel = self.VEL
        self.rect = pygame.Rect(x - radius, y - radius, 2 * radius, 2 * radius)

    def draw(self, screen):
        pygame.draw.circle(screen, self.COLOR, (self.x, self.y), self.radius)

    def set_vel(self, x_vel, y_vel):
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel = 3
        self.y_vel = self.VEL
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def check_bottom_collision(self):
        return self.y + self.radius > HEIGHT - 15


class Brick:
    COLORS = [RED, ORANGE, GREEN, YELLOW]

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x + 15, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def reset(self):
        self.rect = self.rect
        self.color = self.color


bricks = []


def create_bricks():
    brick_width = (WIDTH - 40) // 14
    brick_height = 10
    top_offset = 100

    for row in range(8):
        brick_color = Brick.COLORS[row // 2 % len(Brick.COLORS)]
        for col in range(13):
            brick = Brick(col * (brick_width + 5), top_offset + row * (brick_height + 5), brick_width, brick_height,
                          brick_color)
            bricks.append(brick)


def draw_bricks(screen):
    for brick in bricks:
        brick.draw(screen)


def collision(ball, paddle, brick_list, score):
    bounce_sound = pygame.mixer.Sound('assets/bounce.wav')
    bounce_sound.set_volume(volume)

    # Check for collisions with paddle
    if (paddle.y <= ball.y <= paddle.y + paddle.height and
            paddle.x <= ball.x <= paddle.x + paddle.width):
        ball.y_vel *= -1
        bounce_sound.play()

    # Check for collisions with screen boundaries
    if ball.x - ball.radius <= 15 or ball.x + ball.radius >= WIDTH - 15:
        ball.set_vel(ball.x_vel * -1, ball.y_vel)
        bounce_sound.play()

    if ball.y + ball.radius >= HEIGHT - 15 or ball.y - ball.radius <= 15:
        ball.set_vel(ball.x_vel, ball.y_vel * -1)
        bounce_sound.play()

    if ball.check_bottom_collision():
        return True

    for brick in brick_list:
        if ball.rect.colliderect(brick.rect):
            ball.y_vel *= -1
            brick_list.remove(brick)
            bounce_sound.play()
            break


def movement(keys, paddle):
    if keys[pygame.K_a] and paddle.x - paddle.VEL >= 0:
        paddle.move(up=True)
    if keys[pygame.K_d] and paddle.x + paddle.width + paddle.VEL <= WIDTH:
        paddle.move(up=False)


def restart_game(brick_list, ball, paddle, score):
    for brick in brick_list:
        brick.reset()
    ball.reset()
    paddle.reset()
    create_bricks()
    score = 0
    return ball, paddle, brick_list, score


pygame.mixer.music.load("assets/i_wonder.wav")
scoring_sound = pygame.mixer.Sound('assets/point.wav')
victory_sound = pygame.mixer.Sound('assets/win_music.wav')
defeat_sound = pygame.mixer.Sound('assets/lose_music.wav')
pygame.mixer.music.set_volume(0.3)
scoring_sound.set_volume(volume)
victory_sound.set_volume(volume)
defeat_sound.set_volume(volume)


def draw(screen, paddles, ball, score):
    screen.fill(WHITE)

    # Draw border around the entire game area
    pygame.draw.rect(screen, BLACK, (15, 15, WIDTH - 30, TOP_BLACK_SPACE + 15))
    pygame.draw.rect(screen, BLACK, (15, TOP_BLACK_SPACE, WIDTH - 30, HEIGHT - 15))

    score_text = FONT.render(f"{score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 100 - score_text.get_width() // 2, TOP_BLACK_SPACE + 10))

    draw_bricks(screen)

    for paddle in paddles:
        paddle.draw(screen)

    ball.draw(screen)

    pygame.display.update()


def main():
    global bricks

    game_loop = True
    clock = pygame.time.Clock()
    pygame.mixer.music.play(-1)

    paddle = Paddle(WIDTH // 2, HEIGHT - 125, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    create_bricks()

    won = False
    lost = False
    score = 0
    restart_text_font = pygame.font.Font(None, 20)
    restart_text = restart_text_font.render("PRESS SPACE TO RESTART", True, WHITE)

    while game_loop:
        clock.tick(FPS)

        if not lost:
            draw(SCREEN, [paddle], ball, score)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_loop = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ball, paddle, bricks, score = restart_game(bricks, ball, paddle, score)

            keys = pygame.key.get_pressed()
            movement(keys, paddle)
            ball.move()

            if collision(ball, paddle, bricks, score):
                pygame.mixer.music.pause()
                SCREEN.fill(BLACK)
                pygame.display.update()
                lost = True

            win_text = ' '
            if score == WINNING_SCORE:
                won = True
                win_text = 'YOU WON!'
                victory_sound.play()

            if won:
                pygame.mixer.music.pause()
                SCREEN.fill(BLACK)
                win_text = 'YOU WIN!'
                SCREEN.blit(restart_text,
                            (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 - restart_text.get_height() // 2))
                text = FONT.render(win_text, True, WHITE)
                SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 200))
                won = False
                pygame.display.update()

            if lost:
                pygame.mixer.music.pause()
                SCREEN.fill(BLACK)
                SCREEN.blit(restart_text,
                            (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 - restart_text.get_height() // 2))
                text = FONT.render(win_text, True, WHITE)
                SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 50))
                text = FONT.render("YOU LOST!", True, WHITE)
                SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 200))
                pygame.display.update()

                space_pressed = False
                while not space_pressed:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            game_loop = False
                            space_pressed = True
                            pygame.mixer.pause()

                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                pygame.mixer.pause()
                                pygame.mixer.music.play()
                                ball, paddle, bricks, score = restart_game(bricks, ball, paddle, score)
                                draw(SCREEN, [paddle], ball, score)
                                pygame.display.update()
                                lost = False
                                space_pressed = True


if __name__ == '__main__':
    main()

