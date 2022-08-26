import pygame
from random import sample, choice
from copy import deepcopy; from time import time; from math import sin; from os import walk

I = [[1,1,1,1]], (0,190,225)
J = [[1,0,0],[1,1,1]], (60,60,230)
L = [[0,0,1],[1,1,1]], (220,150,50)
O = [[1,1],[1,1]], (240,215,0)
S = [[0,1,1],[1,1,0]], (135,220,130)
T = [[0,1,0],[1,1,1],[0,0,0]], (110,40,230)
Z = [[1,1,0],[0,1,1]], (220,60,90)

SHAPES  = I, J, L, O, S, T, Z
COLOR   = (20,20,20), (30,30,30), (255,255,255)

class Tetromino:
      def __init__(self,pos,shape):
          self.pos = pygame.Vector2(pos)
          self.shape, self.color = shape

      def rotate(self,player):
          offset = pygame.Vector2()
          backup, self.shape = self.shape, [[self.shape[y][x] for y in range(len(self.shape))]
          for x in range(len(self.shape[0]) - 1,-1,-1)]

          if not player.is_legal(self):
             offset.x = (player.w - len(self.shape[0])) - self.pos.x
             self.pos.x += 1
             if player.is_legal(self): offset.x = player.w - offset.x - 1
             self.pos.x -= 1
             self.pos += offset
             if not player.is_legal(self): self.shape = backup; self.pos -= offset
          if backup != self.shape: SFX["rotate"].play()

      def convert_shape(self):
          return [(int(self.pos.x + x),int(self.pos.y + y))
          for y, row in enumerate(self.shape) for x, col in enumerate(row) if col]

class Player:
      def __init__(self,size,controls):
          self.surface, self.direction = pygame.display.get_surface(), pygame.Vector2()
          self.w, self.h = size; self.controls = controls
          self.game_init(); self.last_time = [time() for _ in range(5)]

      def game_init(self):
          self.board, self.bag = [[None for _ in range(self.w)] for _ in range(self.h)], sample(SHAPES,len(SHAPES))
          self.new_shape, self.score, self.level, self.lines = False, 0, 0, 0
          pygame.mixer.music.load(choice(ls("assets/music"))[1]); pygame.mixer.music.play(-1)
          self.update_bag(); self.refresh_phantom(); self.update_gravity()

      def update_bag(self):
          self.t1 = Tetromino([self.w // 2 - 2,self.h - 21],self.bag.pop(-1))
          if len(self.bag) == 1: self.bag = sample(SHAPES,len(SHAPES))
          self.t2 = Tetromino((self.w + 3 - len(self.bag[-1][0][0]) / 2,self.h - 17),self.bag[-1])

      def update_gravity(self):
          self.GRAVITY = pygame.event.custom_type()
          pygame.time.set_timer(self.GRAVITY,int(1000 / (self.level + 1) + 200))

      def update_scores(self):
          new_lines = self.clear_lines(); self.lines += new_lines
          self.score += [40,100,300,1200,0][new_lines - 1] * (self.level + 1) + self.bonus * (self.level + 1)
          if self.level != self.lines // 10:
             self.level = self.lines // 10; self.update_gravity(); SFX["level"].play()

      def clear_lines(self):
          cleared_lines = [i for i in range(len(self.board)) if not None in self.board[i]]

          if cleared_lines:
             for x in range(self.w):
                 for y in cleared_lines:
                     self.draw_tile(self.pos(x,y),None,False); self.draw_tile(self.pos(x,y),self.board[y][x],True)
                 pygame.display.update(); pygame.time.wait(20)
             pygame.time.wait(50)
          for y in cleared_lines:
              self.board.remove(self.board[y])
              self.board = [[None for _ in range(self.w)]] + self.board

          if len(cleared_lines) > 3: SFX["tetris"].play()
          elif len(cleared_lines): SFX["clear"].play()
          return len(cleared_lines)

      def is_legal(self,shape):
          legal_pos = [(x,y) for y in range(len(self.board)) for x in range(len(self.board[0])) if self.board[y][x] is None]
          for pos in shape.convert_shape():
              if not pos in legal_pos: return False
          return True

      def refresh_phantom(self):
          self.p1 = deepcopy(self.t1)
          while self.is_legal(self.p1): self.p1.pos.y += 1
          self.p1.pos.y -= 1

      def draw_board(self):
          for y in range(len(self.board)):
              for x in range(len(self.board[y])): self.draw_tile(self.pos(x,y),self.board[y][x],False)

      def draw_tetromino(self,shape,phantom):
          for y, row in enumerate(shape.shape):
              for x, col in enumerate(row):
                  if col: self.draw_tile(self.pos(*shape.pos,[x,y]),shape.color,phantom)

      def draw_tile(self,pos,color,phantom):
          rect, border = pygame.Rect(*pos,TILE,TILE).inflate(1,1), 1 if phantom else 0
          if color is not None:
             if RAINBOW: color = abs(sin(self.new_time)) * 255, abs(sin(self.new_time + 2)) * 255, abs(sin(self.new_time + 4)) * 255
             if not phantom: pygame.draw.rect(self.surface,[i // 1.5 for i in color],rect)
             pygame.draw.rect(self.surface,color,rect.inflate(-TILE // 6,-TILE // 6),border)
          else: pygame.draw.rect(self.surface,COLOR[0],rect)
          pygame.draw.rect(self.surface,COLOR[1],rect,1)

      def run(self):
          self.new_time, keys = time(), pygame.key.get_pressed()
          if keys[self.controls[0]] and self.new_time - self.last_time[0] >= 0.2: self.last_time[0] = self.new_time; self.t1.rotate(self)
          if keys[self.controls[1]] and self.new_time - self.last_time[1] >= 0.03: self.last_time[1], self.bonus, self.direction.y = self.new_time, 2, 1
          if keys[self.controls[2]] and self.new_time - self.last_time[2] >= 0.25:
             self.last_time[2], self.bonus, self.t1.pos, self.new_shape = self.new_time, 3, self.p1.pos, True
          if keys[self.controls[3]] != keys[self.controls[4]]:
             if keys[self.controls[3]] and self.new_time - self.last_time[3] >= 0.12: self.last_time[3], self.direction.x = self.new_time, -1
             if keys[self.controls[4]] and self.new_time - self.last_time[4] >= 0.12: self.last_time[4], self.direction.x = self.new_time, 1

          self.t1.pos.x += self.direction.x
          if not self.is_legal(self.t1): self.t1.pos.x -= self.direction.x
          elif self.direction.x: SFX["move"].play()
          self.t1.pos.y += self.direction.y
          if not self.is_legal(self.t1): self.t1.pos.y -= self.direction.y; self.new_shape = True

          self.draw_board(); self.draw_tetromino(self.t1,False); self.draw_tetromino(self.t2,False)
          self.refresh_phantom(); self.draw_tetromino(self.p1,True)
          for text, val, pos in ("Level",self.level,12), ("Lines",self.lines,8), ("Score",self.score,4):
              blit(txt(text),self.pos(self.w + 3,self.h - pos)); blit(txt(str(val)),self.pos(self.w + 3,self.h - pos + 1.5))

          if self.new_shape:
             self.new_shape = False; SFX["freeze"].play()
             for x, y in self.t1.convert_shape(): self.board[y][x] = self.t1.color

             if len(set(self.board[-21])) > 1:
                pygame.mixer.music.stop(); SFX["blockout"].play()
                for y in range(-21,0,1):
                    self.board[y] = [sample(range(0,255),3) for _ in range(self.w)]
                    self.draw_board(); pygame.display.update(); pygame.time.wait(70)
                pygame.time.wait(1000); self.game_init()
             self.update_bag(); self.update_scores(); self.update_gravity()

          self.direction, self.bonus = pygame.Vector2(), 0

      def pos(self,x,y,offset=(0,0)): return (offset[0] + x) * TILE, (offset[1] + y - (self.h - 20)) * TILE

def txt(text): return FONT.render(text,True,COLOR[2])
def blit(content,center_pos): SURFACE.blit(content,content.get_rect(center=center_pos))
def ls(path): return [(file.split(".")[0], "/".join([root,file])) for root,_,files in walk(path) for file in files]

if __name__ == "__main__":
   pygame.init(); PAUSED, RAINBOW, BOARD_SIZE = False, False, (10,24)
   try:
    pygame.mixer.init(); pygame.mixer.music.set_volume(0.3)
    SOUND, SFX = True, dict([(name, pygame.mixer.Sound(path)) for name, path in ls("assets/sfx")])
   except: SOUND = False

   TILE = pygame.display.Info().current_h // 25
   SURFACE = pygame.display.set_mode((abs(TILE) * (BOARD_SIZE[0] + 6),abs(TILE) * 20 + 1))
   SIZE = SURFACE.get_size()

   FONT = pygame.font.Font("assets/font.ttf",SIZE[1] // 25)
   ICON = pygame.image.load("assets/icon.png").convert_alpha()
   pygame.display.set_caption("Tetris")
   pygame.display.set_icon(ICON)

   PLAYER = Player(BOARD_SIZE,(pygame.K_w, pygame.K_s, pygame.K_SPACE, pygame.K_a, pygame.K_d))
   while True:
         for event in pygame.event.get():
             if event.type == pygame.QUIT: pygame.quit(); raise SystemExit
             if event.type == PLAYER.GRAVITY and not PAUSED: PLAYER.direction.y = 1
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1 and not PAUSED: RAINBOW = not RAINBOW
                if event.key == pygame.K_ESCAPE:
                   SFX["pause"].play()
                   if PAUSED: pygame.mixer.music.unpause(); PAUSED = False
                   else: pygame.mixer.music.pause(); PAUSED = True

         SURFACE.fill(COLOR[1])
         blit(txt("Pause"),[i / 2 for i in SIZE]) if PAUSED else PLAYER.run()
         pygame.display.update()
