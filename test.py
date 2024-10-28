import numpy as np

class Class1:
    def __init__(self) -> None:
        self.var1 = None
        self._var5 = None
    @property
    def Var5(self):
        return self._var5
    def load(self,):
        self.var3 = self.var1
        if (self.var1 is None):
            self.var1 = np.zeros((3,3))
        else:
            self.var1 = np.ones((3,3))
        self._var5 = "TEst"
    def print_variables(self,):
        print("var1: ",self.var1)
        print("var3: ",self.var3)


obj1 = Class1()
var6 = obj1.Var5
print(var6)
obj1.load()
print(var6)
obj1.print_variables()
obj1.load()
obj1.print_variables()




