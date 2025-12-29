import pygame
import glob
import os

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
GROUND_HEIGHT = 100
BLOCK_SIZE = 20
GRID_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

class Block:
    def __init__(self, x, y, width, height, block_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = block_type  # 'red' or 'green'
    
    def draw(self, screen, camera_x):
        color = RED if self.type == 'red' else GREEN
        pygame.draw.rect(screen, color, (self.x - camera_x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x - camera_x, self.y, self.width, self.height), 2)

class Editor:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Geometry Dash Level Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        self.blocks = []
        self.finish_x = 1000
        self.camera_x = 0
        self.has_changes = False
        self.selected_tool = 'red'  # 'red', 'green', 'delete', 'finish'
        self.block_width = 60  # Default block width
        self.block_height = 60  # Default block height
        self.dragging_block = None
        self.dragging_finish = False
        self.resizing_block = None
        self.resize_mode = None  # 'width', 'height', 'both'
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.filename = None
        self.state = 'home'  # 'home' or 'editing'
        self.selected_level_index = 0
        self.level_files = []
        
    def load_level(self, filename):
        self.blocks = []
        self.finish_x = 1000
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) == 5:
                            x, y, width, height, block_type = parts
                            self.blocks.append(Block(int(x), int(y), int(width), int(height), block_type.strip()))
                        elif len(parts) == 2 and parts[0] == 'FINISH':
                            self.finish_x = int(parts[1])
            self.filename = filename
            self.has_changes = False
        except FileNotFoundError:
            print(f"File {filename} not found")
    
    def save_level(self, filename):
        with open(filename, 'w') as f:
            f.write("# Level created with Geometry Dash Editor\n")
            for block in self.blocks:
                f.write(f"{block.x},{block.y},{block.width},{block.height},{block.type}\n")
            if self.finish_x is not None:
                f.write(f"FINISH,{self.finish_x}\n")
        self.filename = filename
        print(f"Level saved as {filename}")
    
    def refresh_level_list(self):
        self.level_files = glob.glob("level*.txt") + ["Create New Level"]
        if self.selected_level_index >= len(self.level_files):
            self.selected_level_index = 0
    
    def draw_home_screen(self):
        self.screen.fill(BLACK)
        
        # Title
        title = pygame.font.Font(None, 48).render("LEVEL EDITOR", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        # Level list
        for i, level_file in enumerate(self.level_files):
            color = WHITE if i == self.selected_level_index else GRAY
            level_text = self.font.render(f"{i + 1}. {level_file}", True, color)
            y_pos = 200 + i * 40
            self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, y_pos))
            
            # Cursor
            if i == self.selected_level_index:
                pygame.draw.rect(self.screen, WHITE, (WIDTH // 2 - level_text.get_width() // 2 - 20, y_pos, 10, 30))
        
        # Instructions
        instructions = self.font.render("UP/DOWN to select, ENTER to edit", True, WHITE)
        self.screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))
    
    def start_editing_level(self):
        if self.selected_level_index < len(self.level_files) - 1:
            # Load existing level
            self.load_level(self.level_files[self.selected_level_index])
        else:
            # Create new level
            self.blocks = []
            self.finish_x = 1000
            self.filename = None
        self.state = 'editing'
    
    def get_resize_mode(self, block, world_x, mouse_y):
        # Check if clicking near edges for resizing
        edge_threshold = 5
        
        near_right = abs(world_x - (block.x + block.width)) < edge_threshold
        near_bottom = abs(mouse_y - (block.y + block.height)) < edge_threshold
        near_left = abs(world_x - block.x) < edge_threshold
        near_top = abs(mouse_y - block.y) < edge_threshold
        
        if (near_right or near_left) and (near_bottom or near_top):
            return 'both'
        elif near_right or near_left:
            return 'width'
        elif near_bottom or near_top:
            return 'height'
        return None
    
    def handle_mouse_down(self, pos):
        mouse_x, mouse_y = pos
        world_x = mouse_x + self.camera_x
        
        # Check if clicking on finish line
        if self.finish_x and abs(world_x - self.finish_x) < 10 and mouse_y < HEIGHT - GROUND_HEIGHT:
            if self.selected_tool == 'delete':
                self.finish_x = None  # Remove finish line
                self.has_changes = True
            else:
                self.dragging_finish = True
                self.drag_offset_x = world_x - self.finish_x
            return
        
        # Check if clicking on existing block
        for block in self.blocks:
            if (block.x <= world_x <= block.x + block.width and 
                block.y <= mouse_y <= block.y + block.height):
                if self.selected_tool == 'delete':
                    self.blocks.remove(block)
                    self.has_changes = True
                    return
                
                # Check if clicking near edge for resizing
                resize_mode = self.get_resize_mode(block, world_x, mouse_y)
                if resize_mode:
                    self.resizing_block = block
                    self.resize_mode = resize_mode
                    self.drag_offset_x = world_x
                    self.drag_offset_y = mouse_y
                else:
                    # Start dragging block
                    self.dragging_block = block
                    self.drag_offset_x = world_x - block.x
                    self.drag_offset_y = mouse_y - block.y
                return
        
        # Create new block if not clicking on existing one
        if self.selected_tool in ['red', 'green']:
            snap_x = self.snap_to_grid(world_x)
            snap_y = self.snap_to_grid(mouse_y)
            self.blocks.append(Block(snap_x, snap_y, self.block_width, self.block_height, self.selected_tool))
            self.has_changes = True
        elif self.selected_tool == 'finish' and self.finish_x is None:
            # Create new finish line
            self.finish_x = self.snap_to_grid(world_x)
            self.has_changes = True
    
    def handle_mouse_up(self, pos):
        self.dragging_block = None
        self.dragging_finish = False
        self.resizing_block = None
        self.resize_mode = None
    
    def snap_to_grid(self, value):
        return (value // 20) * 20
    
    def handle_mouse_motion(self, pos):
        mouse_x, mouse_y = pos
        world_x = mouse_x + self.camera_x
        
        if self.dragging_block:
            # Drag block to new position
            new_x = self.snap_to_grid(world_x - self.drag_offset_x)
            new_y = self.snap_to_grid(mouse_y - self.drag_offset_y)
            if self.dragging_block.x != new_x or self.dragging_block.y != new_y:
                self.has_changes = True
            self.dragging_block.x = new_x
            self.dragging_block.y = new_y
        elif self.dragging_finish:
            # Drag finish line
            new_x = self.snap_to_grid(world_x - self.drag_offset_x)
            if self.finish_x != new_x:
                self.has_changes = True
            self.finish_x = new_x
        elif self.resizing_block:
            # Resize block
            old_width, old_height = self.resizing_block.width, self.resizing_block.height
            if self.resize_mode in ['width', 'both']:
                new_width = max(20, world_x - self.resizing_block.x)
                self.resizing_block.width = self.snap_to_grid(new_width)
            if self.resize_mode in ['height', 'both']:
                new_height = max(20, mouse_y - self.resizing_block.y)
                self.resizing_block.height = self.snap_to_grid(new_height)
            if old_width != self.resizing_block.width or old_height != self.resizing_block.height:
                self.has_changes = True
    
    def draw_grid(self):
        # Draw grid
        for x in range(-self.camera_x % GRID_SIZE, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT - 100), 1)
        for y in range(0, HEIGHT - 100, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y), 1)
    
    def draw_toolbox(self):
        # Toolbox background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (10, 10, 400, 150))
        pygame.draw.rect(self.screen, BLACK, (10, 10, 400, 150), 2)
        
        # Tool buttons
        tools = [('red', RED), ('green', GREEN), ('delete', WHITE), ('finish', BLUE)]
        for i, (tool, color) in enumerate(tools):
            x = 20 + i * 45
            y = 20
            # Highlight selected tool
            if tool == self.selected_tool:
                pygame.draw.rect(self.screen, BLACK, (x-2, y-2, 34, 24), 2)
            pygame.draw.rect(self.screen, color, (x, y, 30, 20))
            if tool == 'delete':
                pygame.draw.line(self.screen, BLACK, (x+5, y+5), (x+25, y+15), 2)
                pygame.draw.line(self.screen, BLACK, (x+25, y+5), (x+5, y+15), 2)
        
        # Save button
        save_color = GREEN if self.has_changes else GRAY
        pygame.draw.rect(self.screen, save_color, (220, 20, 60, 30))
        pygame.draw.rect(self.screen, BLACK, (220, 20, 60, 30), 2)
        save_text = self.font.render("SAVE", True, BLACK)
        self.screen.blit(save_text, (235, 27))
        
        # Home button
        pygame.draw.rect(self.screen, BLUE, (290, 20, 60, 30))
        pygame.draw.rect(self.screen, BLACK, (290, 20, 60, 30), 2)
        home_text = self.font.render("HOME", True, WHITE)
        self.screen.blit(home_text, (305, 27))
        
        # Width controls
        width_text = self.font.render(f"Width: {self.block_width}", True, BLACK)
        self.screen.blit(width_text, (20, 60))
        
        pygame.draw.rect(self.screen, WHITE, (20, 80, 20, 20))
        pygame.draw.rect(self.screen, BLACK, (20, 80, 20, 20), 1)
        minus_text = self.font.render("-", True, BLACK)
        self.screen.blit(minus_text, (27, 83))
        
        pygame.draw.rect(self.screen, WHITE, (50, 80, 20, 20))
        pygame.draw.rect(self.screen, BLACK, (50, 80, 20, 20), 1)
        plus_text = self.font.render("+", True, BLACK)
        self.screen.blit(plus_text, (56, 83))
        
        # Height controls
        height_text = self.font.render(f"Height: {self.block_height}", True, BLACK)
        self.screen.blit(height_text, (20, 110))
        
        pygame.draw.rect(self.screen, WHITE, (20, 130, 20, 20))
        pygame.draw.rect(self.screen, BLACK, (20, 130, 20, 20), 1)
        minus_text2 = self.font.render("-", True, BLACK)
        self.screen.blit(minus_text2, (27, 133))
        
        pygame.draw.rect(self.screen, WHITE, (50, 130, 20, 20))
        pygame.draw.rect(self.screen, BLACK, (50, 130, 20, 20), 1)
        plus_text2 = self.font.render("+", True, BLACK)
        self.screen.blit(plus_text2, (56, 133))
        
        # Instructions
        text = self.font.render("Drag blocks/finish, resize at edges", True, BLACK)
        self.screen.blit(text, (200, 70))
        
        # Camera position
        cam_text = self.font.render(f"Camera: {self.camera_x}", True, BLACK)
        self.screen.blit(cam_text, (200, 90))
        
        # Filename
        if self.filename:
            file_text = self.font.render(f"File: {self.filename}", True, BLACK)
            self.screen.blit(file_text, (200, 110))
    
    def draw_ground(self):
        # Draw ground
        pygame.draw.rect(self.screen, GREEN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        pygame.draw.line(self.screen, WHITE, (0, HEIGHT - GROUND_HEIGHT), (WIDTH, HEIGHT - GROUND_HEIGHT), 2)
    
    def draw_finish_line(self):
        if self.finish_x is not None:
            finish_screen_x = self.finish_x - self.camera_x
            if -10 < finish_screen_x < WIDTH + 10:
                pygame.draw.line(self.screen, BLUE, (finish_screen_x, 0), (finish_screen_x, HEIGHT - GROUND_HEIGHT), 5)
                # Label
                text = self.font.render("FINISH", True, BLUE)
                self.screen.blit(text, (finish_screen_x - 25, 10))
    
    def draw_player_start(self):
        start_x = 150 - self.camera_x
        if -50 <= start_x <= WIDTH + 50:
            # Draw player start indicator
            player_y = HEIGHT - GROUND_HEIGHT - 30  # Player size is 30
            pygame.draw.rect(self.screen, (0, 255, 255), (start_x, player_y, 30, 30), 2)  # Cyan outline
            text = self.font.render("START", True, (0, 255, 255))
            self.screen.blit(text, (start_x - 10, player_y - 25))
    
    def select_tool_at_pos(self, pos):
        mouse_x, mouse_y = pos
        if 10 <= mouse_y <= 160:  # Toolbox area
            # Save button
            if 220 <= mouse_x <= 280 and 20 <= mouse_y <= 50 and self.has_changes:
                if self.filename:
                    self.save_level(self.filename)
                else:
                    self.save_level("new_level.txt")
                self.has_changes = False
                return
            # Home button
            elif 290 <= mouse_x <= 350 and 20 <= mouse_y <= 50:
                self.state = 'home'
                self.refresh_level_list()
                return
            # Width controls
            elif 20 <= mouse_x <= 40 and 80 <= mouse_y <= 100:  # Width minus
                self.block_width = max(20, self.block_width - 20)
                return
            elif 50 <= mouse_x <= 70 and 80 <= mouse_y <= 100:  # Width plus
                self.block_width = min(200, self.block_width + 20)
                return
            # Height controls
            elif 20 <= mouse_x <= 40 and 130 <= mouse_y <= 150:  # Height minus
                self.block_height = max(20, self.block_height - 20)
                return
            elif 50 <= mouse_x <= 70 and 130 <= mouse_y <= 150:  # Height plus
                self.block_height = min(200, self.block_height + 20)
                return
            # Tool selection
            elif 20 <= mouse_x <= 50 and 20 <= mouse_y <= 40:
                self.selected_tool = 'red'
            elif 65 <= mouse_x <= 95 and 20 <= mouse_y <= 40:
                self.selected_tool = 'green'
            elif 110 <= mouse_x <= 140 and 20 <= mouse_y <= 40:
                self.selected_tool = 'delete'
            elif 155 <= mouse_x <= 185 and 20 <= mouse_y <= 40:
                self.selected_tool = 'finish'
    
    def run(self):
        self.refresh_level_list()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == 'home':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.selected_level_index = (self.selected_level_index - 1) % len(self.level_files)
                        elif event.key == pygame.K_DOWN:
                            self.selected_level_index = (self.selected_level_index + 1) % len(self.level_files)
                        elif event.key == pygame.K_RETURN:
                            self.start_editing_level()
                elif self.state == 'editing':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.camera_x = max(0, self.camera_x - 50)
                        elif event.key == pygame.K_RIGHT:
                            self.camera_x += 50
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            if 10 <= event.pos[1] <= 160:  # Clicking in toolbox
                                self.select_tool_at_pos(event.pos)
                            else:  # Clicking in level area
                                self.handle_mouse_down(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # Left click release
                            self.handle_mouse_up(event.pos)
                    elif event.type == pygame.MOUSEMOTION:
                        self.handle_mouse_motion(event.pos)
            
            # Draw based on state
            if self.state == 'home':
                self.draw_home_screen()
            else:
                # Draw everything
                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_ground()
                
                # Draw blocks
                for block in self.blocks:
                    block.draw(self.screen, self.camera_x)
                
                self.draw_finish_line()
                self.draw_player_start()
                self.draw_toolbox()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def show_file_dialog(self):
        # Simple file selection
        level_files = glob.glob("level*.txt")
        if level_files:
            print("Available levels:")
            for i, f in enumerate(level_files):
                print(f"{i+1}. {f}")
            try:
                choice = int(input("Enter number to load (0 for new): "))
                if choice > 0 and choice <= len(level_files):
                    self.load_level(level_files[choice-1])
            except:
                pass

def main():
    editor = Editor()
    editor.run()

if __name__ == "__main__":
    main()
