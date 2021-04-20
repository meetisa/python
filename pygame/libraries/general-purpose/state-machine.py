import pygame as pg

class State:
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

class StateMachine:
    def __init__(self, **imp):
        self.__dict__.update(imp)
        self.done = False
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        if hasattr(self, 'caption'):
            pg.display.set_caption(self.caption)
        if hasattr(self, 'icon'):
            pg.display.set_icon(self.icon)
        
    def setup(self, state_dict, start_state):
        self.state_dict = state_dict
        self.sn = start_state
        self.state = self.state_dict[self.sn]
        
    def flip(self):
        self.state.done = False
        previous, self.sn = self.sn, self.state.next
        self.state = self.state_dict[self.sn]
        self.state.previous = previous
        
    def update(self):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip()
        return self.state.update(self.screen)
        
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_events(event)

    def game_loop(self):
        while not self.done:
            t = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            if self.update():
                pg.display.update(self.update())
            else:
                pg.display.update()
