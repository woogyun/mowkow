#coding: utf-8

# making the hierarchy of Errors
# To do: enriching the arguments of errors
#        translate into Korean

class ErrLisp(Exception):
    pass

class ErrSyntax(ErrLisp):
    def __init__(self:ErrLisp):
        pass
    def __str__(self:ErrLisp) -> str:
        return "구문 오류"

class ErrUnbound(ErrLisp):
    def __init__(self, sym: str):
        self.symname = sym
    def __str__(self:ErrLisp) -> str:
        return f"이름 '{self.symname}'을(를) 찾을 수 없습니다."

class ErrArgs(ErrLisp):
    def __init__(self, fun: str):
        self.funname = fun
    def __str__(self:ErrLisp) -> str:
        return f"함수 {self.funname}: 인수 개수 오류입니다."

class ErrType(ErrLisp):
    def __init__(self, fun: str):
        self.funname = fun
    def __str__(self:ErrLisp) -> str:
        return f"함수 {self.funname}: 타입 오류입니다."
