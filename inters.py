import json

# Intlist implements a list of inters in a JSON file
class Intlist:

    def __init__(self, path):
        self.path = path
        pass

    def add_int(self, name):
        
        with open(self.path) as intlist:
            inters = json.load(intlist)

        if inters.get(name):
            inters[name] += 1
            with open(self.path, 'w') as intlist:
                json.dump(inters, intlist)
        else:
            inters[name] = 1
            with open(self.path, 'w') as intlist:
                json.dump(inters, intlist)

    def get_inters(self):
        with open(self.path) as intlist:
            inters = json.load(intlist)
            return inters

    def reset(self):
        with open(self.path) as intlist:
            inters = json.load(intlist)
            inters.clear()
        with open(self.path, 'w') as intlist:
            json.dump(inters, intlist)