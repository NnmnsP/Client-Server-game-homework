import pygame
from queue import Queue

pygame.init()

info = pygame.display.Info()
# screen_width = info.current_w
# screen_height = info.current_h
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Pygame Project")

font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()

running = True

def prepare_image(file_name, scale, angle):
    img = pygame.image.load(file_name)
    img.convert()
    img = pygame.transform.rotozoom(img, angle, scale)
    img.set_colorkey("black")
    return img

class Bullet:
    def __init__(self, x, y, speed_x, speed_y, color) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.width = 100
        self.height = 100

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # status text on screen on the right
        # print('Bullet draw')
        screen.blit(font.render(f"X: {0}, Y: {0}, Speed X: {self.speed_x}, Speed Y: {self.speed_y}", True, (255, 255, 255)), (screen_width - 300, 0))


    def update(self, dt):
        self.x += self.speed_x 
        self.y += self.speed_y 

        # if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
        #     return True

class Player:
    def __init__(self, images_files, scale, angle) -> None:
        self.x = 0
        self.y = 0
        self.color = "red"
        self.speed_x = 0
        self.speed_y = 0
        self.acceleration = 1
        self.images = []
        self.image_index = 0
        for filename in images_files:
            self.images.append(prepare_image(f"images/{filename}", scale, angle))

        self.image = self.images[self.image_index]
        self.width = self.images[self.image_index].get_width()
        self.height = self.images[self.image_index].get_height()

    def draw(self):
        # pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        screen.blit(self.image, (self.x, self.y))
        # add status text on screen
        #screen.blit(font.render(f"X: {self.x}, Y: {self.y}, Speed X: {self.speed_x}, Speed Y: {self.speed_y}, Acceleration: {self.acceleration}", True, (255, 255, 255)), (0, 0))

    def update(self, dt):
        self.x += self.speed_x * self.acceleration * dt
        self.y += self.speed_y * self.acceleration * dt

        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.width:
            self.x = screen_width - self.width
        
        if self.y < 0:
            self.y = 0
        elif self.y > screen_height - self.height:
            self.y = screen_height - self.height

        # update the image index
        self.image_index += 1
        self.image_index %= len(self.images)

        self.image = self.images[self.image_index]

    def move(self, direction):
        if direction == "up":
            self.speed_y = -1
        elif direction == "down":
            self.speed_y = 1
        elif direction == "left":
            self.speed_x = -1
        elif direction == "right":
            self.speed_x = 1

    # boost the player for 5 seconds
    def boost(self):
        self.acceleration = 2
        pygame.time.set_timer(pygame.USEREVENT, 5000)
        
        # schedule the resetAcceleration function to be called in 5 seconds
        pygame.time.set_timer(pygame.USEREVENT + 1, 5000)

    def resetAcceleration(self):
        self.acceleration = 1


player_list = []
# player = Player(['e-ship1.png', 'e-ship2.png', 'e-ship3.png'])
player_list.append(Player(['e-ship1.png', 'e-ship2.png', 'e-ship3.png'], 0.5, 0))
player_list.append(Player(['ship1.png', 'ship2.png', 'ship3.png'], 0.5, 180))

dt = 0

# key_pressed_list = []

up_pressed = False
down_pressed = False
left_pressed = False
right_pressed = False

w_pressed = False
s_pressed = False
a_pressed = False
d_pressed = False
bullet_list = []

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                up_pressed = True
            elif event.key == pygame.K_DOWN:
                down_pressed = True
            elif event.key == pygame.K_LEFT:
                left_pressed = True
            elif event.key == pygame.K_RIGHT:
                right_pressed = True
            elif event.key == pygame.K_w:
                w_pressed = True
            elif event.key == pygame.K_s:
                s_pressed = True
            elif event.key == pygame.K_a:
                a_pressed = True
            elif event.key == pygame.K_d:
                d_pressed = True
            elif event.key == pygame.K_SPACE:
                # player.boost()
                for player in player_list:
                    player.boost()
            elif event.key == pygame.K_c:
                # create a bullet
                bullet_list.append(Bullet(player_list[0].x, player_list[0].y, 0, -1, "red"))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up_pressed = False
            elif event.key == pygame.K_DOWN:
                down_pressed = False
            elif event.key == pygame.K_LEFT:
                left_pressed = False
            elif event.key == pygame.K_RIGHT:
                right_pressed = False
            elif event.key == pygame.K_w:
                w_pressed = False
            elif event.key == pygame.K_s:
                s_pressed = False
            elif event.key == pygame.K_a:
                a_pressed = False
            elif event.key == pygame.K_d:
                d_pressed = False
        elif event.type == pygame.USEREVENT:
            if event.type == pygame.USEREVENT:
                for player in player_list:
                    player.resetAcceleration()


    

    if up_pressed:
        player_list[0].move("up")
    elif down_pressed:
        player_list[0].move("down")
    elif left_pressed:
        player_list[0].move("left")
    elif right_pressed:
        player_list[0].move("right")

    if w_pressed:
        player_list[1].move("up")
    elif s_pressed:
        player_list[1].move("down")
    elif a_pressed:
        player_list[1].move("left")
    elif d_pressed:
        player_list[1].move("right")

    screen.fill('teal')

    for player in player_list:
        player.update(dt)
        player.draw()
    for bullet in bullet_list:
        bullet.update(dt)
        bullet.draw()
    # player.printStatus()
    # player.move()

    pygame.display.flip()

    clock.tick(60)

    dt = clock.tick(60)

pygame.quit()