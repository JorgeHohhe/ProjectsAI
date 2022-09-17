import pygame
import math
import numpy as np
import time

pygame.font.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Maximaze a function")

ROWS = 2
COLUMNS = 2
NUM_RANDOM_POINTS = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

NORMALIZATION = 16

START_POSITION = [0,0]
END_POSITION = [1,1]

LEARNING_RATE = 1
TEXT_FONT = pygame.font.SysFont('arial', 24)


# Function to maximaze
def function(x, y):
    term_1 = 4*math.exp(-(x**2 + y**2 - 2*(x + y - 1)))
    term_2 = math.exp(-((x - 3)**2 + (y - 3)**2))
    term_3 = math.exp(-((x + 3)**2 + (y - 3)**2))
    term_4 = math.exp(-((x - 3)**2 + (y + 3)**2))
    term_5 = math.exp(-((x + 3)**2 + (y + 3)**2))
    return term_1 + term_2 + term_3 + term_4 + term_5


def generate_random_start_points(num):
    np.random.seed(0)

    start_points = []
    for i in range(num):
        start_points.append([(np.random.random()-0.5)*NORMALIZATION, (np.random.random()-0.5)*NORMALIZATION])
    # print(start_points)
    return start_points


def look_directions(point, learning_rate):
    possible_paths = [point, [point[0]+learning_rate, point[1]], [point[0]-learning_rate, point[1]], [point[0], point[1]+learning_rate], [point[0], point[1]-learning_rate]]
    function_values = []
    for path in possible_paths:
        function_values += [function(path[0], path[1])]
    # print(function_values)
    chosed_path = possible_paths[function_values.index(max(function_values))]
    # print(chosed_path)
    return chosed_path


def algorithm(points):
    global LEARNING_RATE
    while LEARNING_RATE > 0.1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        points_to_check = []
        for point in points[-NUM_RANDOM_POINTS:]:
            points_to_check += [look_directions(point, LEARNING_RATE)]
        if points[-NUM_RANDOM_POINTS:] == points_to_check:
            LEARNING_RATE /= 2
            print('Decreasing learning rate:', LEARNING_RATE)
        draw(WIN, points)
        points += points_to_check
        time.sleep(0.25)
    
    orange_points = points[-NUM_RANDOM_POINTS:][:]
    flag_global_max = True
    while orange_points != []:
        function_values = []
        for point in orange_points:
            function_values += [function(point[0], point[1])]
        max_function_value = max(function_values)
        chosed_path = orange_points[function_values.index(max_function_value)]
        orange_points = [point for point in orange_points if math.sqrt((point[0]-chosed_path[0])**2 + (point[1]-chosed_path[1])**2) > LEARNING_RATE*2]
        if flag_global_max:
            print('\nGlobal Max:', max_function_value, chosed_path)
            flag_global_max = False
        else:
            print('Local Max:', max_function_value, chosed_path)
        
    print('\nFinished!')
    return False


def draw_grid(win, rows, columns, width):
    pygame.draw.line(win, GREY, (0, width // 2), (width, width // 2))
    pygame.draw.line(win, GREY, (width // 2, 0), (width // 2, width))

    gap = width//NORMALIZATION

    for i in range(NORMALIZATION):
        pygame.draw.line(win, GREY, (gap*i, width//2-5), (gap*i, width//2+5))
        pygame.draw.line(win, GREY, (width//2-5, gap*i), (width//2+5, gap*i))
        if i < 8:
            text = TEXT_FONT.render('-'+chr(-i+8+48), 1, (10, 10, 10))
        else:
            text = TEXT_FONT.render(chr(i-8+48), 1, (10, 10, 10))
        win.blit(text, (gap*i-8, WIDTH//2-30))
        win.blit(text, (WIDTH//2-25, gap*i-16))


def draw(win, points):
    win.fill(WHITE)

    last_points = points[-NUM_RANDOM_POINTS:]
    for point in points:
        x = (point[0] + 8) * WIDTH/NORMALIZATION
        y = (point[1] + 8) * WIDTH/NORMALIZATION
        # print(point)
        pygame.draw.circle(win, TURQUOISE, (x, y), 10)
    for point in last_points:
        x = (point[0] + 8) * WIDTH/NORMALIZATION
        y = (point[1] + 8) * WIDTH/NORMALIZATION
        # print(point)
        pygame.draw.circle(win, ORANGE, (x, y), 10)

    draw_grid(win, ROWS, COLUMNS, WIDTH)
    pygame.display.update()


def main(win, width):
    global LEARNING_RATE
    start_points = generate_random_start_points(NUM_RANDOM_POINTS)
    points = start_points[:]

    run = True
    while run:
        draw(win, points)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    algorithm(points)

                # Restart the game when press key "R"
                if event.key == pygame.K_r:
                    LEARNING_RATE = 1
                    points = start_points[:]
                    draw(win, points)
                    print('Restarted!')

    pygame.quit()

main(WIN, WIDTH)