import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

BLACK_GRID = [[0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],[0,9],
            [0,10],[0,11],[0,12],[0,13],[0,14],[0,15],[0,16],[0,17],[0,18],[0,19],[0,20],[0,21],[0,22],
            [1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],
            [11,0],[12,0],[13,0],[14,0],[15,0],[16,0],[17,0],[18,0],[19,0],[20,0],[21,0],[22,0],[23,0],[24,0],
            [11,1],[15,1],[24,1],
            [5,2],[11,2],[13,2],[20,2],[24,2],
            [4,3],[14,3],[15,3],[18,3],
            [4,4],[5,4],[6,4],[9,4],[20,4],
            [1,5],[2,5],[9,5],[23,5],
            [24,6],
            [6,7],[11,7],[12,7],[22,7],
            [3,8],[8,8],[12,8],
            [1,9],[2,9],[11,9],[21,9],
            [2,10],[3,10],[7,10],[12,10],[18,10],[23,10],
            [3,11],[4,11],[7,11],
            [7,12],[10,12],[12,12],[22,12],[24,12],
            [6,13],[10,13],[17,13],[18,13],[19,13],[22,13],
            [2,14],[11,14],[15,14],[24,14],
            [1,15],[12,15],[13,15],
            [3,16],[7,16],[10,16],[14,16],[17,16],[19,16],[23,16],
            [9,17],[22,17],
            [2,18],[3,18],[8,18],[10,18],[19,18],[20,18],[21,18],[23,18],
            [5,19],[8,19],[10,19],[13,19],[22,19],
            [11,21],[15,21],[21,21]]
START_POSITION = [1, 1]
END_POSITION = [24, 21]

class Spot:
	def __init__(self, row, col, width, height, total_rows, total_columns):
		self.row = row
		self.col = col
		self.x = row * height
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.height = height
		self.total_rows = total_rows
		self.total_columns = total_columns

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.height, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_columns - 1 and not grid[self.row + 1][self.col].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # UP
			self.neighbors.append(grid[self.row][self.col - 1])


# Heuristic (Absolute Distance)
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			start.make_start()
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, columns, width):
	grid = []
	gap_x = width // rows
	gap_y = width // columns
	for i in range(columns):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap_x, gap_y, rows, columns)
			if [i, j] in BLACK_GRID:
				spot.make_barrier()
			elif [i, j] == START_POSITION:
				spot.make_start()
				start_spot = spot
			elif [i, j] == END_POSITION:
				spot.make_end()
				end_spot = spot
			grid[i].append(spot)

	return grid, start_spot, end_spot


def draw_grid(win, rows, columns, width):
	gap_x = width // rows
	gap_y = width // columns
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap_x), (width, i * gap_x))
		for j in range(columns):
			pygame.draw.line(win, GREY, (j * gap_y, 0), (j * gap_y, width))


def draw(win, grid, rows, columns, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, columns, width)
	pygame.display.update()


def main(win, width):
	ROWS = 22
	COLUMNS = 25
	grid, start, end = make_grid(ROWS, COLUMNS, width)

	run = True
	while run:
		draw(win, grid, ROWS, COLUMNS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, COLUMNS, width), grid, start, end)

				# Restart the game when press key "R"
				if event.key == pygame.K_r:
					grid, start, end = make_grid(ROWS, COLUMNS, width)

	pygame.quit()

main(WIN, WIDTH)