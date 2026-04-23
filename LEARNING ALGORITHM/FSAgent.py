from typing import List
from typing import Tuple
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import abc
import math
import pygame as engine
import random
import sys
import time

def distance(tplP1 : Tuple[int, int], tplP2 : Tuple[int, int]) -> float:
    return math.sqrt(math.pow(tplP1[0] - tplP2[0], 2) + math.pow(tplP1[1] - tplP2[1], 2))

class Percept:
    def __init__(self, lstDetails : List):
        self._details = lstDetails

    def __repr__(self) -> str:
        return f"{self.details}"

    def __getitem__(self, intIndex : int):
        return self._details[intIndex]

    @property
    def details(self) -> List:
        return self._details

class Entity:
    def __init__(self, environment, strKey : str, strPath : str):
        r = random.randrange(environment.size) * environment._spriteSize
        c = random.randrange(environment.size) * environment._spriteSize
        self.move((r, c))
        self._environment = environment
        self._key = strKey
        if self._key not in self._environment._assets:
            self._environment._assets[self._key] = engine.image.load(strPath)
    
    def move(self, tplLocation : Tuple[int, int]) -> None:
        self._location = tplLocation
    
    def __repr__(self) -> str:
        return f"{self._key} @ {self.centre}"

    @property
    def location(self) -> Tuple[int, int]:
        return self._location

    @property
    def centre(self) -> Tuple[int, int]:
        r, c = self._location
        s = self._environment._spriteSize // 2
        return (r + s, c + s)

    def draw(self) -> None:
        env = self._environment
        img = env._assets[self._key]
        (r, c) = self._location
        img.set_colorkey((255, 0, 255))
        env._window.blit(img, (r, c))


class Background(Entity):
    def __init__(self, environment, strKey : str, strPath : str):
        super().__init__(environment, strKey, strPath)
        self.move((0,0))
        
    def draw(self) -> None:
        env = self._environment
        img = env._assets['bg']
        s = env._spriteSize
        env._window.blit(img, (0, 0))
        for r in range(env.size):
            for c in  range(env.size):
                target = (r * s, c * s)
                env._window.blit(img, target)

class Dirt(Entity):
    pass

class Hazard(Entity):
    pass

class Power(Entity):
    pass

class State(metaclass=abc.ABCMeta):
    def __init__(self, agent):
        self._agent = agent
        agent._fear = 0
        agent._health = 100
        agent._power = 100

    @abc.abstractmethod
    def __call__(self, percept : Percept) -> int:
        pass

    def getOptions(self) -> List[Tuple[int,int]]:
        env = self._agent._environment
        s = env.size * env._spriteSize
        lstOptions = []
        for r in range(s):
            for c in range(s):
                lstOptions.append((r,c))
        lstOptions = list(filter(lambda p: distance(p, self._agent.centre) <= self._agent.sensorRange, lstOptions))
        return lstOptions
    
    def applyAffect(self, percept : Percept) -> None:
        if self._agent._fear > 0:
            self._agent._power -= 1
        if self._agent._fear > 0:
            self._agent._fear -= 1
        lstNear = list(filter(lambda p: p[0] <= env._spriteSize, percept.details))
        lstDust = list(filter(lambda p: isinstance(p[1], Dirt), lstNear))
        for d in lstDust:
            self._agent._environment.removeAt('dirt', d[1].location)
        lstHazard = list(filter(lambda p: isinstance(p[1], Hazard), lstNear))    
        self._agent._health -= 10 * len(lstHazard)
        self._agent._health = max(self._agent._health, 0)
        if(self._agent._health <= 0):
            print("Agent lost")
            sys.exit()
        lstPower = list(filter(lambda p: isinstance(p[1], Power), lstNear))
        if len(lstPower) > 0:
            self._agent._power = 100
            self._agent._environment.removeAt('power', lstPower[0][1].location)

        

class Wander(State):
    def __init__(self, agent):
        super().__init__(agent)
        self._id = 0

    def __call__(self, percept : Percept) -> int:
        print("Wandering")
        lstOptions = self.getOptions()
        tplDest = random.choice(lstOptions)
        self._agent.move(tplDest)
        self.applyAffect(percept)
        r = random.randint(0, 99)
        if(r <= self._agent._fear):
            return 1
        if(r > self._agent._power):
            return 2
        for p in percept.details:
            if isinstance(p[1], Dirt):
                return 3
        
        return self._id

class Flee(State):
    def __init__(self, agent):
        super().__init__(agent)
        self._id = 1

    def __call__(self, percept : Percept) -> int:
        print("Fleeing")
        lstHazard = []
        for p in percept.details:
            if isinstance(p[1], Hazard):
                lstHazard.append(p)
        if len(lstHazard) == 0:
            return 0
        
        lstHazard.sort(key=lambda t: t[0])
        h = lstHazard[0]
        lstOptions = self.getOptions()
        lstDistances = [(distance(o, h[1].centre), o) for o in lstOptions]
        lstDistances.sort(key=lambda t: t[0])
        self._agent.move(lstDistances[-1][1])
        return self._id

class Charge(State):
    def __init__(self, agent):
        super().__init__(agent)
        self._id = 2

    def __call__(self, percept : Percept) -> int:
        print("Seeking power")
        lstPower = []
        for p in percept.details:
            if isinstance(p[1], Power):
                lstPower.append(p)
        if len(lstPower) == 0:
            return 0
        
        lstPower.sort(key=lambda t: t[0])
        p = lstPower[0]
        lstOptions = self.getOptions()
        lstDistances = [(distance(o, p[1].centre), o) for o in lstOptions]
        lstDistances.sort(key=lambda t: t[0])
        self._agent.move(lstDistances[0][1])
        return self._id


class Clean(State):
    def __init__(self, agent):
        super().__init__(agent)
        self._id = 3
    
    def __call__(self, percept : Percept) -> int:
        print("Moving to clean")
        lstDirt = []
        for p in percept.details:
            if isinstance(p[1], Dirt):
                lstDirt.append(p)
        if len(lstDirt) == 0:
            return 0
        
        lstDirt.sort(key=lambda t: t[0])
        d = lstDirt[0]
        lstOptions = self.getOptions()
        lstDistances = [(distance(o, d[1].centre), o) for o in lstOptions]
        lstDistances.sort(key=lambda t: t[0])
        self._agent.move(lstDistances[0][1])
        return self._id

class Environment:
    def __init__(self, intSize : int, intSpriteSize : int, intDirt : int, intPower : int, intHazard : int):
        engine.init()
        engine.display.set_caption("FSA-based agents")
        engine.display.set_icon(engine.image.load('Assets/terminal.png'))
        self._size = intSize
        self._spriteSize = intSpriteSize
        self._assets = {}
        self._entities = {}
        self._entities['bg'] = Background(self, 'bg', 'Assets/tile.bmp')
        self._entities['dirt'] = []
        for _ in range(intDirt):
            self._entities['dirt'].append(Dirt(self, 'dirt', 'Assets/dirt.bmp'))
        self._entities['hazard'] = []
        for _ in range(intHazard):
            self._entities['hazard'].append(Hazard(self, 'hazard', 'Assets/hazard.bmp'))
        self._entities['power'] = []
        for _ in range(intPower):
            self._entities['power'].append(Power(self, 'power', 'Assets/power.bmp'))
        self._entities['agent'] = Agent(self, 'agent', 'Assets/agent.bmp')
        self._window = engine.display.set_mode((self.size * intSpriteSize, self.size * intSpriteSize))

    def removeAt(self, strKey : str, tplWhere : Tuple[int, int]) -> None:
        print(f"Removing {strKey} @ {tplWhere}")
        lstEntities = self._entities[strKey]
        for i in range(len(lstEntities)):
            if lstEntities[i].location == tplWhere:
                del lstEntities[i]
                return
    
    def run(self):
        self._continue = True
        while self._continue:
            self.draw()
            self._entities['agent'].act()
            for event in engine.event.get():
                if event.type == engine.QUIT:
                    engine.quit()
                    self._continue = False

    @property
    def size(self):
        return self._size

    @property
    def entities(self) -> List:
        es = []
        for k in self._entities.keys():
            if k in ['dirt', 'hazard', 'power']:
                for e in self._entities[k]:
                    es.append(e)
            else:
                es.append(self._entities[k])
        return es

    def draw(self):
        for e in self.entities:
            e.draw()
        size = self.size * self._spriteSize
        surface = engine.Surface((size, size), engine.SRCALPHA, 32)
        colour = (0, 0, 255, 85)
        agent = self._entities['agent']
        pos = agent.centre
        engine.draw.circle(surface, colour, pos, agent.sensorRange)
        self._window.blit(surface, (0,0))
        engine.display.flip()

class Agent(Entity):
    def __init__(self, environment, strKey : str, strPath : str, dblRange : float = 192):
        super().__init__(environment, strKey, strPath)
        self._range = dblRange
        self._state = 1
        self._states = []
        self._states.append(Wander(self))
        self._states.append(Flee(self))
        self._states.append(Charge(self))
        self._states.append(Clean(self))


    @property
    def sensorRange(self) -> float:
        return self._range
    
    def sense(self) -> Percept:
        ds = [(distance(self.centre, e.centre), e) for e in self._environment.entities]
        ds = list(filter(lambda d: (d[0] <= self.sensorRange) and (d[0] > 0), ds))
        p = Percept(ds)
        print(p)
        return p
    
    def act(self) -> None:
        state = self._states[self._state]
        p = self.sense()
        self._state = state(p)
        state.applyAffect(p)

if __name__ == "__main__":
    env = Environment(10, 64, 10, 2, 3)
    env.run()