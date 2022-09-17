import pygame
import time
from copy import copy, deepcopy

pygame.font.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Akari Solver")

TEXT_FONT = pygame.font.SysFont('arial', 50)

ROWS = 7
COLUMNS = 7

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

SLEEP_TIMER = 0.25
 
GRID_GAME_1 = [{'pos': [0,4], 'char': ''},
			   {'pos': [1,2], 'char': '0'},{'pos': [1,3], 'char': '0'},
			   {'pos': [2,0], 'char': '1'},{'pos': [2,5], 'char': '3'},
			   {'pos': [3,1], 'char': '0'},{'pos': [3,3], 'char': ''},{'pos': [3,5], 'char': '1'},
			   {'pos': [4,1], 'char': ''},{'pos': [4,6], 'char': ''},
			   {'pos': [5,3], 'char': ''},{'pos': [5,4], 'char': '1'},
			   {'pos': [6,2], 'char': '2'}]

GRID_GAME_2 = [{'pos': [0,2], 'char': '1'},
			   {'pos': [1,4], 'char': ''},
			   {'pos': [2,1], 'char': ''},{'pos': [2,3], 'char': '4'},{'pos': [2,6], 'char': '1'},
			   {'pos': [3,2], 'char': '4'},{'pos': [3,4], 'char': '3'},
			   {'pos': [4,0], 'char': '1'},{'pos': [4,3], 'char': '2'},{'pos': [4,5], 'char': ''},
			   {'pos': [5,2], 'char': '1'},
			   {'pos': [6,4], 'char': '2'}]

GRID_GAME_3 = [{'pos': [0,4], 'char': '0'},
			   {'pos': [1,1], 'char': '4'},{'pos': [1,5], 'char': ''},
			   {'pos': [2,0], 'char': ''},
			   {'pos': [4,6], 'char': ''},
			   {'pos': [5,1], 'char': '1'},{'pos': [5,5], 'char': '2'},
			   {'pos': [6,2], 'char': '2'},]

class Spot:
	def __init__(self, row, col, width, height, total_rows, total_columns):
		self.row = row
		self.col = col
		self.char = ''
		self.seen = False
		self.x = row * height
		self.y = col * width
		self.color = WHITE
		self.width = width
		self.height = height
		self.total_rows = total_rows
		self.total_columns = total_columns

	def already_seen(self):
		self.seen = True

	def get_pos(self):
		return self.row, self.col

	def reset(self):
		self.color = WHITE

	def is_barrier(self):
		return self.color == BLACK

	def is_lamp(self):
		return self.color == RED

	def is_bright(self):
		return self.color == YELLOW

	def is_blocked(self):
		return self.color == PURPLE

	def is_nothing(self):
		return self.color == WHITE

	def is_restricted(self):
		return self.is_lamp() or self.is_barrier() or self.is_bright() or self.is_blocked()

	def make_bright(self):
		self.color = YELLOW

	def set_char(self, char):
		self.char = char

	def make_lamp(self, grid):
		self.color = RED
		self.update_neighbors(grid)

	def make_barrier(self):
		self.color = BLACK

	def make_blocked(self):
		self.color = PURPLE

	def draw(self, win):
		if self.is_lamp():
			pygame.draw.rect(win, YELLOW, (self.x, self.y, self.height, self.width))
			pygame.draw.circle(win, BLACK, (self.x + self.height/2, self.y + self.width/2), 45)
			pygame.draw.circle(win, WHITE, (self.x + self.height/2, self.y + self.width/2), 40)
		else:
			pygame.draw.rect(win, self.color, (self.x, self.y, self.height, self.width))
		
		if self.char != '':
			self.char = int(self.char)
			text = TEXT_FONT.render(chr(self.char +48), 1, (255, 255, 255))
			win.blit(text, (self.x + self.height/2-12, self.y + self.width/2-25))

	def blocked_spots(self, grid):
		if self.char == self.look_near_neighbors(grid, 'lamp'):
			if self.row < self.total_columns - 1 and not grid[self.row + 1][self.col].is_restricted(): # RIGHT
				grid[self.row + 1][self.col].make_blocked()
			if self.row > 0 and not grid[self.row - 1][self.col].is_restricted(): # LEFT
				grid[self.row - 1][self.col].make_blocked()
			if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_restricted(): # DOWN
				grid[self.row][self.col + 1].make_blocked()
			if self.col > 0 and not grid[self.row][self.col - 1].is_restricted(): # UP
				grid[self.row][self.col - 1].make_blocked()

	def update_neighbors(self, grid):
		row, col = 1, 1
		while self.row < self.total_columns - row and not grid[self.row + row][self.col].is_barrier(): # RIGHT
			spot = grid[self.row + row][self.col]
			spot.make_bright()
			row += 1

		row, col = 1, 1
		while self.row - row + 1 > 0 and not grid[self.row - row][self.col].is_barrier(): # LEFT
			spot = grid[self.row - row][self.col]
			spot.make_bright()
			row += 1

		row, col = 1, 1
		while self.col < self.total_rows - col and not grid[self.row][self.col + col].is_barrier(): # DOWN
			spot = grid[self.row][self.col + col]
			spot.make_bright()
			col += 1

		row, col = 1, 1
		while self.col - col + 1 > 0 and not grid[self.row][self.col - col].is_barrier(): # UP
			spot = grid[self.row][self.col - col]
			spot.make_bright()
			col += 1

	def look_near_neighbors(self, grid, spot_type):
		possible_positions = 0
		if spot_type == 'restricted':
			if self.row < self.total_columns - 1 and not grid[self.row + 1][self.col].is_restricted(): # RIGHT
				possible_positions += 1
			if self.row > 0 and not grid[self.row - 1][self.col].is_restricted(): # LEFT
				possible_positions += 1
			if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_restricted(): # DOWN
				possible_positions += 1
			if self.col > 0 and not grid[self.row][self.col - 1].is_restricted(): # UP
				possible_positions += 1
			return possible_positions + self.look_near_neighbors(grid, 'lamp')
		elif spot_type == 'lamp':
			if self.row < self.total_columns - 1 and grid[self.row + 1][self.col].is_lamp(): # RIGHT
				possible_positions += 1
			if self.row > 0 and grid[self.row - 1][self.col].is_lamp(): # LEFT
				possible_positions += 1
			if self.col < self.total_rows - 1 and grid[self.row][self.col + 1].is_lamp(): # DOWN
				possible_positions += 1
			if self.col > 0 and grid[self.row][self.col - 1].is_lamp(): # UP
				possible_positions += 1
			return possible_positions

	def make_near_neighbors_lamp(self, draw, grid):
		if self.row < self.total_columns - 1 and not grid[self.row + 1][self.col].is_restricted(): # RIGHT
			grid[self.row + 1][self.col].make_lamp(grid)
			draw()
			time.sleep(SLEEP_TIMER)
		if self.row > 0 and not grid[self.row - 1][self.col].is_restricted(): # LEFT
			grid[self.row - 1][self.col].make_lamp(grid)
			draw()
			time.sleep(SLEEP_TIMER)
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_restricted(): # DOWN
			grid[self.row][self.col + 1].make_lamp(grid)
			draw()
			time.sleep(SLEEP_TIMER)
		if self.col > 0 and not grid[self.row][self.col - 1].is_restricted(): # UP
			grid[self.row][self.col - 1].make_lamp(grid)
			draw()
			time.sleep(SLEEP_TIMER)


def game_ended(grid):
	for row in grid:
		for spot in row:
			if spot.is_nothing() or spot.is_blocked():
				return False
			if spot.is_barrier() and spot.char != '' and spot.look_near_neighbors(grid, 'lamp') != spot.char:
				return False
	return True


def respecting_constrains(grid):
	for row in grid:
		for spot in row:
			if spot.is_barrier() and spot.char != '' and spot.look_near_neighbors(grid, 'lamp') > spot.char:
				return False
	
	return True


# Backtracking Implementation
def back_tracking(grid, assignment):
	# Initializate
	initial_grid = deepcopy(grid)
	for spot in assignment:
		x, y = spot.get_pos()
		grid[x][y].make_lamp(grid)
	# Check if game ended
	if game_ended(grid):
		return True, assignment
	
	# Generating candidate spots (all white spots)
	candidates = []
	for row in grid:
		for spot in row:
			spot.blocked_spots(grid)
			if spot.is_nothing():
				candidates += [spot]
	
	draw(WIN, grid, ROWS, COLUMNS, WIDTH)
	time.sleep(SLEEP_TIMER)

	grid = deepcopy(initial_grid)
	for spot in candidates:
		# Generating the grid with assigned spots
		for spot2 in assignment:
			x, y = spot2.get_pos()
			grid[x][y].make_lamp(grid)
		x, y = spot.get_pos()
		grid[x][y].make_lamp(grid)
		# Testing restrictions
		if respecting_constrains(grid):
			assignment += [spot]
			if back_tracking(grid, assignment)[0]:
				return True, assignment
			assignment.remove(spot)
		grid = deepcopy(initial_grid)
	
	return False, assignment


# Verificacao Fowarding + Heuristic
def algorithm(draw, grid):
	# Initializate blocked spots
	for row in grid:
		for spot in row:
			spot.blocked_spots(grid)	
	draw()
	time.sleep(SLEEP_TIMER)

	flag_end = False
	while not flag_end:
		flag_end = True
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			
		# Check with black spots restrictions
		for row in grid:
			for spot in row:
				if spot.is_barrier() and spot.char != '' and spot.char != 0 and not spot.seen:
					if int(spot.char) == spot.look_near_neighbors(grid, 'restricted'):
						print(spot.char, spot.row, spot.col)
						spot.make_near_neighbors_lamp(draw, grid)
						spot.already_seen()
						flag_end = False
					spot.blocked_spots(grid)
					draw()
					time.sleep(SLEEP_TIMER)

	print('Backtracking')
	answer = back_tracking(grid, [])[1]

	for spot in answer:
		x, y = spot.get_pos()
		grid[x][y].make_lamp(grid)
		draw()
		time.sleep(SLEEP_TIMER)

	print('Finished')
	return grid


def make_grid(rows, columns, width, grid_game):
	grid = []
	gap_x = width // rows
	gap_y = width // columns
	POSITIONS_GAME_1 =  [a['pos'] for a in grid_game]
	CHARS_GAME_1 =  [a['char'] for a in grid_game]
	for i in range(columns):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap_x, gap_y, rows, columns)
			if [i, j] in POSITIONS_GAME_1:
				spot.make_barrier()
				spot.set_char(CHARS_GAME_1[POSITIONS_GAME_1.index([i, j])])
			grid[i].append(spot)

	return grid


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
	grid_game = GRID_GAME_1
	grid = make_grid(ROWS, COLUMNS, width, grid_game)

	run = True
	flag_next_grid = False
	while run:
		draw(win, grid, ROWS, COLUMNS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and flag_next_grid:
					# Alternate game pressing "WHITESPACE"
					if grid_game == GRID_GAME_1:
						grid_game = GRID_GAME_2
						print('Grid of Game 2 Selected!')
					elif grid_game == GRID_GAME_2:
						grid_game = GRID_GAME_3
						print('Grid of Game 3 Selected!')
					elif grid_game == GRID_GAME_3:
						grid_game = GRID_GAME_1
						print('Grid of Game 1 Selected!')
					grid = make_grid(ROWS, COLUMNS, width, grid_game)
					flag_next_grid = False
				if event.key == pygame.K_SPACE and not flag_next_grid:
					grid = algorithm(lambda: draw(win, grid, ROWS, COLUMNS, width), grid)
					flag_next_grid = True

				# Change and Restart the game when press key "R"
				if event.key == pygame.K_r:
					grid = make_grid(ROWS, COLUMNS, width, grid_game)
					flag_next_grid = False

	pygame.quit()

main(WIN, WIDTH)
