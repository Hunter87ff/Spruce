

class Test:
    def __init__(self):
        self._name="something"

    @property
    def name(self):
        return self._name
    
    @property
    def relation(self):
        return False
    
    @name.setter
    def name(self, value):
        self._name = value

    

i1 = Test()

print(i1.name)
i1.name = "RT"
print(i1.name)