class Image:

    ROTATE_180 = 1

    @classmethod
    def open(cls, name):
        self = cls()
        self.name = name
        self.format = 1
        return self

    def transpose(self, t):
        return self

    def save(self, filename, format=None):
        with open(filename, "wb") as f:
            f.write(self.name.encode('utf-8'))
