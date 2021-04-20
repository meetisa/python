import pygame as pg
import spritesheet
from random import choice
from funzione import os_command
import time
from itertools import cycle
import clustering
import numpy as np
from text import Text

class Campo:
    def __init__(self, namesurf, surf):
        """Classe per il campo"""
        self.surf = spritesheet.SpriteSheet(surf, 'file')

        # Prendo le misure dell'immagine
        size = surf.get_size()

        self.square_size = 30

        # Calcolo il numero di righe e di colonne
        self.raws = range(int(size[1]/self.square_size))
        self.columns = range(int(size[0]/self.square_size))

        # Calcolo i colori dominanti attravero un algoritmo           
        # chiamato "k-means clustering"
        self.color = clustering.Kmeans(5).run(namesurf)

            
        self.color.sort(key = lambda x: sum(x))
        self.color = self.color[::-1]

        self.back, self.cflags, self.lines, self.cmine, self.numbers = self.color
        


    def build(self, screen, n_mine):
        """Per costuire il campo di gioco,
        per piazzare le mine e quindi calcolare quale
        numero avrà ogni quadrato
        """

        # Il campo è costituito da due Layer diversi:
        # Quello più sopra è composto dall'immagine
        # In quello più sotto ci sono i numeri o niente
        self.sopra = self.surf.load_grid(len(self.raws), len(self.columns))
        self.sotto = [[None for column in self.columns] for raw in self.raws]
        
        # Numero di mine
        self.mine = n_mine

        # Numero di bandiere piazzate
        self.nflags = 0

        # Se la partita è finita o no
        self.done = False

        # Booleano per sapere se un quadrato è stato scoperto
        self.cliccati = [[False for column in self.columns] for raw in self.raws]

        # Booleano per sapere se una bandiera è stata posta
        self.flags = [[False for column in self.columns] for raw in self.raws]

        # Booleano per sapere se il curso è posizionato su un quadrato
        self.mouse_is_there = [[False for column in self.columns] for raw in self.raws]


        # Piazzo le mine in modo causale
        for _ in range(n_mine):
            while True:
                r = choice(self.raws)
                c = choice(self.columns)
                if self.sotto[r][c] != 'mina':
                    self.sotto[r][c] = 'mina'
                    break

        # Carico i rect dei quadrati e i numeri
        x_square = 0
        y_square = 0
        self.rect = []
        for ir in self.raws:
            self.rect.append([])
            for ic in self.columns:
                if self.sotto[ir][ic] == None:
                    # Calcolo quante mine ci sono nei quadrati adiacenti
                    mine = sum([1 for square in self.borders(ir,ic,'values') if square == 'mina'])

                    if mine != 0:
                        self.sotto[ir][ic] = Text(str(mine),
                                                  size = int(self.square_size-self.square_size/3),
                                                  color = self.numbers)
                    else:
                        self.sotto[ir][ic] = None
                  
                self.rect[-1].append(pg.Rect(x_square, y_square,
                                             self.square_size, self.square_size))
                x_square += self.square_size
            x_square = 0
            y_square += self.square_size



    def update(self, event):
        """In questa funzione vengono analizzati tutti
        gli eventi che il giocatore provoca:
        in questo caso bisogna occuparsi solo di quando
        clicca il mouse
        """
        for ir in self.raws:
            for ic in self.columns:

                clicked = self.cliccati[ir][ic]
                flags = self.flags[ir][ic]

                # Rilevo su quale quadrato è il cursore
                if self.rect[ir][ic].collidepoint(pg.mouse.get_pos()):

                    self.mouse_is_there[ir][ic] = True

                    # Rilevo se si clicca il mouse
                    if event.type == pg.MOUSEBUTTONDOWN:

                        # Se si clicca il tasto sinistro
                        if event.button == 1 and not clicked and not flags:
                            if self.scopre(ir, ic):
                                pg.time.delay(1000)
                                self.done = True
                                return 'perdita'

                        # Se si clicca il tasto centrale (rotella)
                        if event.button == 2:
                            if clicked:
                                for r, c in self.borders(ir, ic, 'indexes'):
                                    if not self.flags[r][c]:
                                        if self.scopre(r, c):
                                            pg.time.delay(1000)
                                            self.done = True
                                            return 'perdita'
                                        else:
                                            self.cliccati[r][c] = True

                        # Se si clicca il tasto destro
                        if event.button == 3:
                            if 0 <= self.nflags < self.mine and not clicked:
                                self.flags[ir][ic] = not self.flags[ir][ic]
                                self.nflags = sum([1 for _ in self.flags for b in _ if b])
                                os_command('cancella lo schermo')
                                print('Mine rilevate: {}    |    Mine mancanti: {}'.format(self.nflags, self.mine - self.nflags))
                else:
                    self.mouse_is_there[ir][ic] = False
            
        nclicked = sum([1 for _ in self.cliccati for c in _ if c])
        
        if nclicked == len(self.raws)*len(self.columns) - self.mine:        
            pg.time.delay(1000)
            self.done = True
            return 'vittoria'


    def borders(self, r, c, mode):
        """Restituisce una lista con i valori o le coordinate dei quadrati
        adiacenti al quadrato delle coordinate date;
        il parametro mode decide cosa restituire
        """
        coords = [(-1,-1), (-1,0), (-1,1),
                  (0, -1),          (0,1),
                  (1, -1), (1, 0), (1, 1)]
        if mode == 'indexes':
            return [(r+x,c+y) for x, y in coords
                           if 0 <= r+x < len(self.raws) and 0 <= c+y < len(self.columns)]
        else:
            return [self.sotto[r+x][c+y] for x, y in coords
                           if 0 <= r+x < len(self.raws) and 0 <= c+y < len(self.columns)]

    def scopre(self, r, c):
        """Calcola se il quadrato delle coordinate date è vuoto:
        Se il quadrato in questione è una mine restituisce vero,
        invece  se è vuoto scopre il layer sopra di tutti i
        quadrati vuoti adiacenti a sè e di tutti gli altri,
        fino a quando non si incontra un numero o una mina.
        """
        if self.sotto[r][c] != 'mina':
            if not self.flags[r][c]:
                self.cliccati[r][c] = True
                if self.sotto[r][c] == None:
                    for ir, ic in self.borders(r, c, 'indexes'):
                        if self.flags[ir][ic]:
                            continue
                        if self.sotto[ir][ic] is None and not self.cliccati[ir][ic]:
                            self.scopre(ir, ic)
                        self.cliccati[ir][ic] = True
        else:
            return True


    def render(self, screen):
        """Per renderizzare il campo,
        Se la partita è finita si visualizza solo il secondo layer
        """
        screen.fill(self.back)
        x = 0
        y = 0
        
        for ir, raw in enumerate(self.sopra):
            for ic, column in enumerate(raw):

                # minimizzo le variabili per una questione estetica
                rect = self.rect[ir][ic]
                clicked = self.cliccati[ir][ic]
                sotto = self.sotto[ir][ic]
                flags = self.flags[ir][ic]
                mouse = self.mouse_is_there[ir][ic]
                
                if clicked or self.done:
                    try:
                        # Disegno i numeri
                        sotto.render(screen, None, int(rect.x + self.square_size/2) + 1,
                                                   int(rect.y + self.square_size/2) + 1, 'center')
                    except AttributeError:
                        # Disegno le mine
                        if sotto == 'mina':
                            pg.draw.circle(screen, self.cmine,
                                           (int(rect.x + self.square_size/2) + 1,
                                            int(rect.y + self.square_size/2) + 1),
                                            int(self.square_size/2 - self.square_size/4)
                                           )
                else:
                    # Renderizzo il quadrato dell'immagine
                    screen.blit(column, rect)

                # Linee orizzontali e verticali per la griglia  
                pg.draw.line(screen, self.lines, (0, y), (screen.get_width(), y), 2)
                pg.draw.line(screen, self.lines, (x, 0), (x, screen.get_height()), 2)

                # Disegno le bandiere
                if flags:
                    pg.draw.rect(screen, self.cflags, (rect.x+6, rect.y+6,
                                                       rect.width-10, rect.height-10))
                    
                # Metto un filtro bianco sul quadrato in cui c'è il cursore
                if mouse and not clicked:
                        s = pg.Surface(rect.size, pg.SRCALPHA)
                        pg.draw.rect(s, (255, 255, 255, 150), s.get_rect())
                        screen.blit(s, rect)

                x += self.square_size
            x = 0
            y += self.square_size
            
