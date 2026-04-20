import pygame
import sys
import random

#Configuración
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 40
FPS = 60

#Colores
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (100,100, 100)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 182, 193) #Color del fantasma

# Mapa del juego 1 pared, 2 = bloque destructible, 0 = vacio, 3 = punto
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,2,2,0,0,0,0,0,2,2,0,0,1],          
    [1,0,1,2,1,0,1,1,1,0,1,2,1,0,1],  
    [1,2,2,2,2,2,2,3,2,2,2,2,2,2,1],  
    [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],          
    [1,0,0,2,2,0,0,0,0,0,2,2,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

class Entidad:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def dibujar(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * TILE_SIZE + 20, self.y * TILE_SIZE + 20), 15)

class Fantasma(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y, PINK)
        self.move_delay = 30
        self.timer = 0

    def mover(self):
        self.timer += 1
        if self.timer >= self.move_delay:
            direcciones = ([(0, 1), (0, -1), (1, 0), (-1, 0)])
            random.shuffle(direcciones)
            for dx, dy in direcciones:
                nx, ny = self.x + dx, self.y + dy
                #El fntasma no puede atravesar paredes
                if MAP[ny][nx] == 0 or MAP[ny][nx] == 3:
                    self.x, self.y = nx, ny
                    break
            self.timer = 0

class Pacman(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW)
        self.bombas = []
        self.vivo = True

    def mover(self, dx, dy):
        if MAP[self.y + dy][self.x + dx] not in [1, 2]:
            self.x += dx
            self.y += dy
            
class Bomba(Entidad):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.timer = 90  # Tiempo para explotar
        self.explota = False
        self.rango = 2

    def actualizar(self, fantasmas, pacman):
        self.timer -= 1
        if self.timer <= 0:
            self.explota = True
            #Logica de explosión
            self.chequear_explosion(fantasmas, pacman)
        return self.timer <= -20
    
    def chequear_explosion(self, fantasmas, pacman):
        puntos_explosion = [(self.x, self.y)]
        for i in range(1, self.rango + 1):
            puntos_explosion.extend([(self.x + i, self.y), (self.x - i, self.y), (self.x, self.y + i), (self.x, self.y - i)])

        for px, py in puntos_explosion:
            #Matar fantasmas
            for f in fantasmas[:]:
                if f.x == px and f.y == py:
                    fantasmas.remove(f)
            #Matar a Pacman
            if pacman.x == px and pacman.y == py:
                pacman.vivo = False
            #Romper paredes
            if 0 <= py < len(MAP) and 0 <= px < len(MAP[0]):
                if MAP[py][px] == 2:
                    MAP[py][px] = 3

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    pman = Pacman(1, 1)
    fantasmas = [Fantasma(13, 1), Fantasma(13, 5), Fantasma(1, 5)]

    while pman.vivo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: pman.mover(0, -1)
                if event.key == pygame.K_DOWN: pman.mover(0, 1)
                if event.key == pygame.K_LEFT: pman.mover(-1, 0)
                if event.key == pygame.K_RIGHT: pman.mover(1, 0)
                if event.key == pygame.K_SPACE:
                    if(len(pman.bombas) < 2): pman.bombas.append(Bomba(pman.x, pman.y))

        #Actualizar fantasmas
        for f in fantasmas:
            f.mover()
            if f.x == pman.x and f.y == pman.y:
                pman.vivo = False

        #Actualizar bombas
        for b in pman.bombas[:]:
            if b.actualizar(fantasmas, pman):
                pman.bombas.remove(b)

        #Dibujar todo
        screen.fill(BLACK)
        for r, fila in enumerate(MAP):
            for c, tile in enumerate(fila):
                rect = (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 1: pygame.draw.rect(screen, BLUE, rect)
                elif tile == 2: pygame.draw.rect(screen, GREY, rect)
                elif tile == 3: pygame.draw.circle(screen, WHITE, (c*TILE_SIZE+20, r*TILE_SIZE+20), 4)

        for b in pman.bombas:
            color = RED if b.explota else (200, 0, 0)
            pygame.draw.circle(screen, color, (b.x * TILE_SIZE + 20, b.y * TILE_SIZE + 20), 15)

        for f in fantasmas: f.dibujar(screen)
        pman.dibujar(screen)

        pygame.display.flip()
        clock.tick(FPS)

    print("GAME OVER - Te han atrapado o te has explotado a ti mismo")
    pygame.quit()

if __name__ == "__main__":
    main()