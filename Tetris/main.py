import pygame
import random
import buttons

pygame.font.init()

dark = (255, 255, 255)
light = (0, 0, 0)

temp_score = 0
high_score = 0

s_width = 600
s_height = 700
play_width = 300
play_height = 600
block_size = 30

top_left_x = (s_width - play_width - 250)
top_left_y = s_height - play_height

window = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Tetris")

menu_font = pygame.font.Font('ImminentLine.ttf', 100)
tetris_main_label = menu_font.render("TETRIS", True, light)

high_font = pygame.font.Font('ImminentLine.ttf', 50)

btn_play = buttons.button(s_width/2 - 80 - 100, 400, 160, 40, light, "Play")
btn_quit = buttons.button(s_width/2 - 80 + 100, 400, 160, 40, light, "Quit")

# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

pygame.mixer.init()
point_sound = pygame.mixer.Sound("point.wav")


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    grid = [[dark for x in range(10)] for x in range(20)]

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                c = locked_positions[(x, y)]
                grid[y][x] = c

    return grid


def convert_shape_format(shape):
    positions = []
    form = shape.shape[shape.rotation % len(shape.shape)]

    for x, line in enumerate(form):
        row = list(line)
        for y, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + x, shape.y + y))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(x, y) for x in range(10) if grid[y][x] == dark] for y in range(20)]
    accepted_pos = [x for sub in accepted_pos for x in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_grid(surface, grid):
    for y in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (top_left_x, top_left_y + y*block_size), (top_left_x + play_width, top_left_y + y*block_size))
        for x in range(len(grid[y])):
            pygame.draw.line(surface, (128, 128, 128), (top_left_x + x*block_size, top_left_y), (top_left_x + x*block_size, top_left_y + play_height))


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    global temp_score
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if dark not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc



def draw_next_shape(shape, surface):
    font = pygame.font.Font('ImminentLine.ttf', 20)
    label = font.render("Next Shape", 1, light)
    score_label = font.render(f'Score: {temp_score}', 1, light)

    form = shape.shape[shape.rotation % len(shape.shape)]

    shape_x = top_left_x + play_width + 50
    shape_y = top_left_y + play_height/2 - 100

    for x, line in enumerate(form):
        row = list(line)
        for y, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(window, shape.color, (shape_x + x*block_size, shape_y + y*block_size, block_size, block_size), 0)

    surface.blit(label, (shape_x - 6, shape_y - 30))
    surface.blit(score_label, (shape_x + 12, shape_y + 160))



def draw_window(surface, grid):
    pygame.font.init()
    surface.fill(dark)
    font = pygame.font.Font('ImminentLine.ttf', 60)
    label = font.render("Tetris", 1, light)
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 0))

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x],
                             (top_left_x + x * block_size, top_left_y + y * block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)

    draw_grid(surface, grid)


def main():
    lock_position = {}
    grid = create_grid(lock_position)

    run = True
    change_piece = False
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27

    while run:
        global temp_score
        grid = create_grid(lock_position)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                lock_position[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            last_score = temp_score
            temp_score += clear_rows(grid, lock_position)
            if temp_score > last_score:
                point_sound.play()

        if check_lost(lock_position):
            run = False



        draw_window(window, grid)
        draw_next_shape(current_piece, window)
        pygame.display.update()
    window.fill(dark)
    pygame.display.update()
    main_menu()


def main_menu():
    loop = True
    while loop:
        window.fill(dark)
        global high_score
        if temp_score > high_score:
            high_score = temp_score
        high_score_label = high_font.render(f'High Score: {high_score}', True, light)
        window.blit(tetris_main_label, (s_width / 2 - tetris_main_label.get_width() / 2, 100))
        window.blit(high_score_label, (s_width / 2 - high_score_label.get_width() / 2, 500))
        btn_play.draw(window, True)
        btn_quit.draw(window, True)
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.MOUSEMOTION:
                if btn_quit.is_over(pos):
                    btn_quit.color = (0, 255, 0)
                else:
                    btn_quit.color = light

                if btn_play.is_over(pos):
                    btn_play.color = (0, 255, 0)
                else:
                    btn_play.color = light
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_quit.is_over(pos):
                    loop = False
                if btn_play.is_over(pos):
                    loop = False
                    main()
        pygame.display.update()


main_menu()  # start game

pygame.quit()
