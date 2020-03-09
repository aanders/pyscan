class Image:
    @classmethod
    def load(cls, name):
        self = cls()
        self.name = name
        return self

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(name)
