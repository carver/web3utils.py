

class WrapCallable:

    def __init__(self, callee, wrapwith):
        self.__callee = callee
        self.__wrapwith = wrapwith

    def __call__(self, *args, **kwargs):
        return self.__wrapwith(self.__callee(*args, **kwargs))
