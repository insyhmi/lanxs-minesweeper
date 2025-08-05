import random
import pygame
import sys
import os

GAME_PATH = os.path.dirname(__file__)
ASSET_FILE = os.path.join(GAME_PATH, 'assets')
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 700
WINDOW_TITLE = "Lanx's Minesweeper"
BOX_SIZE = 30
PADDING = 50

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BACKGROUND = (244, 244, 244)
NUMBER_COLOR = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0), (0, 255, 255), (199, 167, 122), (107, 207, 207), (139, 198, 129)]

class minesweeper:
    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines
        self.flags = 0
        self.cell_count = width * height
        self.mines_position = set()
        self.flagged_cells = set()
        self.clicked_cells = set()
        self.ALLOW_CLICK = True
        self.mine_text = f"Mines: {self.mines-self.flags}"
        self.CELL_DIRECTION = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
        self.grid_start_x = PADDING
        self.grid_start_y = (WINDOW_HEIGHT - (BOX_SIZE * self.height)) // 2

        pygame.init()
        pygame.font.init()
        self.FONT = pygame.font.SysFont('Arial', 20)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.sprite_flag = pygame.image.load(os.path.join(ASSET_FILE, 'flag.png')).convert_alpha()
        self.sprite_flag = pygame.transform.scale(self.sprite_flag, (BOX_SIZE, BOX_SIZE))        
        self.sprite_mine = pygame.image.load(os.path.join(ASSET_FILE, 'mine.png')).convert_alpha()
        self.sprite_mine = pygame.transform.scale(self.sprite_mine, (BOX_SIZE, BOX_SIZE))     
        self.sprite_clicked_mine = pygame.image.load(os.path.join(ASSET_FILE, 'clicked_mine.png')).convert_alpha()
        self.sprite_clicked_mine = pygame.transform.scale(self.sprite_clicked_mine, (BOX_SIZE, BOX_SIZE))     

        # Board setup
        self.board = [[0 for i in range(width)] for j in range(height)]
        
        # Mines setup
        while len(self.mines_position) != mines:
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if (x, y) not in self.mines_position:
                self.mines_position.add((x, y))
                self.board[y][x] = 'M'
                for (i, j) in self.CELL_DIRECTION:
                    if 0 <= i+x < self.width and 0 <= j+y < self.height and self.board[j+y][i+x] != 'M':
                        self.board[j+y][i+x] += 1
        
        # Main window setup
        running = True
        self.screen_setup()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    cell_position = self.get_position(event.pos)
                    if event.button == 1:  
                        self.click_cell(cell_position)
                    elif event.button == 3:
                        self.place_flag(cell_position)
            if self.win():
                print("You win!")
                self.ALLOW_CLICK = False
                running = False
            pygame.display.flip()

        if not running:
            self.quit()

    def screen_setup(self):
        self.screen.fill(BACKGROUND)
        for j in range(self.height):
            for i in range(self.width):
                cell = self.draw_cell((i, j))
                pygame.draw.rect(self.screen, GRAY, cell)
                pygame.draw.rect(self.screen, BLACK, cell, 1)
        self.update_mine_text(0)

    def is_mine(self, pos):
        return self.board[pos[1]][pos[0]] == 'M'
    
    def cell_number(self, pos):
        return self.board[pos[1]][pos[0]] if self.board[pos[1]][pos[0]] != 'M' else -1

    def win(self):
        return self.cell_count == self.mines

    def draw_cell(self, pos):
        x, y = pos
        return pygame.Rect(
            self.grid_start_x + x * BOX_SIZE,
            self.grid_start_y + y * BOX_SIZE,
            BOX_SIZE,
            BOX_SIZE
        )
    
    def update_mine_text(self, num):
        self.flags += num
        self.mine_text = f"Mines: {self.mines-(self.flags)}"
        text_rect = pygame.Rect(self.grid_start_x + 10 * BOX_SIZE + PADDING-10, PADDING, 100, 50)
        pygame.draw.rect(self.screen, WHITE, text_rect)
        mine_text_surface = self.FONT.render(self.mine_text, True, BLACK)
        mine_text_rect = mine_text_surface.get_rect(center=text_rect.center)
        self.screen.blit(mine_text_surface, mine_text_rect)

    def show_mines(self, pos):
        self.ALLOW_CLICK = False
        for x, y in self.mines_position:
            self.screen.blit(self.sprite_mine, (self.grid_start_x + x * BOX_SIZE, self.grid_start_y + y * BOX_SIZE))
            pygame.display.flip()
        x, y = pos
        self.screen.blit(self.sprite_clicked_mine, (self.grid_start_x + x * BOX_SIZE, self.grid_start_y + y * BOX_SIZE))
        pygame.display.flip()

    def get_position(self, pos):
        x, y = pos
        if self.grid_start_x <= x < self.grid_start_x + (BOX_SIZE * self.width) and self.grid_start_y <= y < self.grid_start_y + (BOX_SIZE * self.height):
            j = (y - self.grid_start_y) // BOX_SIZE
            i = (x - self.grid_start_x) // BOX_SIZE
            return (i, j)
        return None
    
    def click_cell(self, pos, chording = True):
        if not pos:
            return
        if pos in self.flagged_cells:
            return
        if not self.ALLOW_CLICK:
            return
        if pos in self.clicked_cells:
            if chording:
                self.chord(pos)
            return
        x, y = pos
        if self.is_mine(pos):
            print("Its a mine")
            self.show_mines(pos)
            return
        self.clicked_cells.add(pos)
        self.cell_count -= 1
        clicked_cell = self.draw_cell(pos)
        pygame.draw.rect(self.screen, WHITE, clicked_cell)
        pygame.draw.rect(self.screen, BLACK, clicked_cell, 1)
        
        cell_number = self.cell_number(pos)
        cell_color = NUMBER_COLOR[cell_number-1]
        if cell_number == 0:
            cell_number = ""
        cell_number_surface = self.FONT.render(f"{cell_number}", True, cell_color)
        cell_number_rect = cell_number_surface.get_rect(center=clicked_cell.center)
        self.screen.blit(cell_number_surface, cell_number_rect)
        pygame.display.update(clicked_cell)
        
        if self.cell_number(pos) == 0:
            for (i, j) in self.CELL_DIRECTION:
                if (x+i, y+j) not in self.clicked_cells and 0 <= i+x < self.width and 0 <= j+y < self.height:
                    self.click_cell((x+i, y+j), chording=False)

    def chord(self, pos):
        x, y = pos
        surrounding_flagged_cells = set()
        for i, j in self.CELL_DIRECTION:
            if (x+i, y+j) in self.flagged_cells:
                surrounding_flagged_cells.add((x+i, y+j))
        if len(surrounding_flagged_cells) == self.cell_number(pos):
            for i, j in self.CELL_DIRECTION:
                if (x+i, y+j) not in surrounding_flagged_cells and 0 <= i+x < self.width and 0 <= j+y < self.height:
                    self.click_cell((x+i, y+j), chording=False)
        
    def place_flag(self, pos):
        if not pos:
            return
        if not self.ALLOW_CLICK:
            return
        if pos in self.clicked_cells:
            return
        x, y = pos
        if pos in self.flagged_cells:
            self.update_mine_text(-1)
            unflagged_cell = self.draw_cell(pos)
            pygame.draw.rect(self.screen, GRAY, unflagged_cell)
            pygame.draw.rect(self.screen, BLACK, unflagged_cell, 1)
            self.flagged_cells.remove(pos)
            return
        self.update_mine_text(1)
        self.flagged_cells.add(pos)
        self.screen.blit(self.sprite_flag, (self.grid_start_x + x * BOX_SIZE, self.grid_start_y + y * BOX_SIZE))
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

minesweeper(20, 20 ,50)