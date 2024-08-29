class Cart():
    def __init__(self):
        self.items = {}

    def append(self, item):
        if item in self.items.keys():
            self.items[item] += 1
        else:
            self.items[item] = 1
        return

    def delete(self, item):
        if item in self.items.keys():
            self.items[item] -= 1
            if self.items[item] <= 0:
                del self.items[item]

        else:
            return

    def view(self):
        keys = []
        for ke, val in self.items.items():
            keys.append(ke)

        return keys
