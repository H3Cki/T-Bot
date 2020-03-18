
class Copy:
    def copy(self):
        c = self.__class__()
        for attr in self.__dict__.items():
            setattr(c,attr[0],attr[1])
        return c