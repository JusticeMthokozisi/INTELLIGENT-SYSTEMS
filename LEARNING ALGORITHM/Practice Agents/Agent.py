from FSMExample import FiniteStateMachine
class Agent:
    def __init__(self):
        self._fsm = FiniteStateMachine(self)
        self._age = 18
        self._thirst = 0
        self._money = 0
        self._enegry = 100

    def act(self):
        while(True):
            self._fsm.update()