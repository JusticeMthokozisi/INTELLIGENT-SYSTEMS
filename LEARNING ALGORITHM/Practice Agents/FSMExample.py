import Agent
class State:
    def __init__(self, intID : int, objAgent : Agent):
        self._id = intID
        self._agent = objAgent
    
    def update(self):
        return self._id
    
class Sleeping(State):
    def __init__(self, intID : int, objAgent : Agent):
        super().__init__(intID, objAgent)
    
    def update(self):
        print(f"Sleeping - Energy = {self._agent._enegry}, Thirst = {self._agent._thirst}, Age = {self._agent._age}, Money = {self._agent._money}")
        self._agent._enegry += 1
        self._agent._thirst += 1
        self._agent._age += 1

        if(self._agent._thirst > 50):
            return 1
        if(self._agent._age > 100):
            return 3

        return self._id
    
class Drinking(State):
    def __init__(self, intID : int, objAgent : Agent):
        super().__init__(intID, objAgent)

    def update(self):
        print(f"Drinking - Energy = {self._agent._enegry}, Thirst = {self._agent._thirst}, Age = {self._agent._age}, Money = {self._agent._money}")
        self._agent._enegry -= 1
        self._agent._thirst -= 1
        self._agent._age += 1
        self._agent._money -= 1

        if(self._agent._enegry < 50):
            return 0
        if(self._agent._money < 50):
            return 2
        if(self._agent._age > 100):
            return 3
        
        return self._id

class Working(State):
    def __init__(self, intID : int, objAgent : Agent):
        super().__init__(intID, objAgent)
    
    def update(self):
        print(f"Working - Energy = {self._agent._enegry}, Thirst = {self._agent._thirst}, Age = {self._agent._age}, Money = {self._agent._money}")
        self._agent._age += 1
        self._agent._thirst += 1
        self._agent._money += 1
        self._agent._enegry -= 1

        if(self._agent._age > 100):
            return 3
        if(self._agent._money > 100):
            return 1
        if(self._agent._enegry < 50):
            return 0
        
        return self._id
        
class Dead(State):
    def __init__(self, intID : int, objAgent : Agent):
        super().__init__(intID, objAgent)
    
    def update(self):
        #print(f"Dead - Age = {self._agent._age}")
        return self._id
            
class FiniteStateMachine:
    def __init__(self, objAgent : Agent):
        self._states = [Sleeping(0, objAgent), Drinking(1, objAgent), Working(2, objAgent), Dead(3, objAgent)]
        self._currentState = 0

    def update(self):
        #print(self._currentState)
        self._currentState = self._states[self._currentState].update()