#!/usr/bin/env python3

import os

# nascondo il messaggio di pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# Uso il pacchetto pygame per fare mini giochi
import pygame as pg
import sys

sys.path.append('include')

import campo
import text
from funzione import os_command
from resize import resize_image

import random as rn
from PIL import Image
from tkinter import Tk
from tkinter.filedialog import askopenfilename

pg.init()

actual_w = pg.display.Info().current_w
actual_h = pg.display.Info().current_h

# All'inizio chiedo all'utente due input:
# L'immagine di sfondo
while 1:
    try:
        Tk().withdraw()
        filename = askopenfilename(title='Scegli un\'immagine', filetypes=[('Images', '*.png *.jpg *.jpeg'),
                                                                          ('All file', '*.*')])
        file = resize_image(Image.open(filename), 600)
        file = pg.image.frombuffer(file.tobytes(), file.size, file.mode)
        break
    except OSError:
        os_command('cancella lo schermo')
        print('Immagine non riconosiuta, riprova')
    except AttributeError:
        sys.exit()

screen = pg.display.set_mode((600,600))

# Per trovare il titolo della finestra tutto le cartelle,
# Infine tolgo l'estensione del file
cap = filename
while cap.find('/') != -1:
    cap = cap[cap.find('/')+1:]
while cap.find('\\') != -1:
    cap = cap[cap.find('\\')+1:]
    
pg.display.set_caption(cap[:cap.find('.')])

# creo i messaggi che vengono renderizzati in caso di perdita o vittoria
perdita = text.Text('Hai perso, che peccato', size = 30)
vittoria = text.Text('Hai vinto, complimenti!', size = 30)

mine = rn.randint(40, 80)

c = campo.Campo(filename, file)

# Costruisco il campo
c.build(screen, mine)

print(f'Mine rilevate: 0    |    Mine mancanti: {mine}')

clock = pg.time.Clock()
ci = 0
done = False
finito = False
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
            break

        if not finito:
            finito = c.update(event)
        elif event.type == pg.KEYDOWN:
            # Quando si finisce una partita
            # si ha la possibilità di cominciarne una nuova,
            # premendo un qualsiasi tasto
            os_command('cancella lo schermo')
            print('Mine rilevate: {}    |    Mine mancanti: {}'.format(0, mine))
            finito = False
            c.build(screen, mine)

    c.render(screen)

    # Il colore dello sfondo di fine partita è arbitrario
    if finito == 'perdita':
        perdita.render(screen, (0, 0, 0, 200))
        os_command('cancella lo schermo')
        print('Premi un tasto qualsiasi per iniziare una nuova partita!')
    elif finito == 'vittoria':
        vittoria.render(screen, (0, 0, 0, 200))
        os_command('cancella lo schermo')
        print('Premi un tasto qualsiasi per iniziare una nuova partita!')
    pg.display.update()
    clock.tick(30)

# chiudo pygame ed esco
pg.quit()
sys.exit()
