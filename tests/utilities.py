class Echo:
    def __init__(self, name=None):
        if not name:
            name = "Echo"
        self.__name = name

    def __getattr__(self, attr):
        return Echo(self.__name + '.' + attr)

    def __hasattr__(self):
        return True

    def __str__(self):
        return self.__name


class Untouchable:
    def __getattr__(self, attr):
        raise Exception("no touching!")
