#coding: utf-8

from _data import *
from _error import *
import re
import io

# Ph 9
#       lex: 문자 ' 처리
#       read_expr: tok이 '인 경우 추가(quote 노드 추가)
#                  car(cdr(qlst))를 재설정하는 것에서 버그가 있었음

# Ph 12. Library
#       read_simple(str): "-1"이나 "+3"도 인식하도록 수정함

# Ph 13. Quasiquotation
#       lex: ","와 ",@", "`"를 인식하도록 수정함
#       read_expr: "`"를 quasiquote로, ","를 unquote로, ",@"를 unquote-splicing으로 바꾸도록 수정함 

# Ph 14. Multiline 처리
#       클래스: Reader
#       전역 변수: YY_reader 추가
#       전역 함수: match 추가, lex -> next_token으로 변경
#       read_list에서 전에 '('를 읽었다는 가정을 없애고 match로 진행함

# 전역변수 reader
YY_reader = None   # The historical prefix "YY_" is attached to make it global

def slurp(path: str) -> str:
    with io.open(path, mode='r', encoding='utf-8') as reader:
        return reader.read()

class Reader:
    def __init__(self):
        self._LA = None
        self._input = ""
        self._column = 0
        self._depth = 0
        self._prompt1 = ">  "
        self._prompt2 = ".. "
    def next_token(self) -> str:        # returns the token and set it to LA
        s = self._input
        eols = ["\n", "\r"]
        ws = [" ", "\t"] + eols
        while s != "":
            if s[0] in ws:
                s = s[1:]
                self._input = s
                self._column += 1
                continue
            if s[0] in ";":
                i = 0
                while s[i] not in eols:
                    i += 1
                s = s[i:]
                self._input = s
                self._column = 0
                continue
            if s.startswith(",@"):      # ",@" should be tested before ","
                tok = ",@"
            elif s[0] in "().',`":
                tok = s[0]
            else:
                toks = re.split(r"[\s()]", s)
                tok = toks[0]
            tlen = len(tok)
            self._input = s[tlen:]
            self._column += tlen
            self._LA = tok
            return tok
        if self._depth > 0:
            self.read2()
            return self.next_token()
        tok = ""
        self._LA = tok
        return tok
    def match(self, tok) -> None:
        if tok != self._LA:
            print(f"ERROR: Lexical Error near '{YY_reader.LA()}'")
    def LA(self) -> str:
        return self._LA
    def read(self) -> str:
        try:
            self._input = input(self._prompt1)
        except EOFError:
            return ""
        else:
            return self._input
    def read2(self) -> str:
        try:
            self._input = input(self._prompt2 + self.indent())
        except EOFError:
            return ""
        else:
            return self._input
    def readfile(self, fname) -> str:
        self._input = slurp(fname)
    def nestin(self) -> None:
        self._depth += 1
    def nestout(self) -> None:
        self._depth -= 1
    def indent(self) -> str:
        return self._depth * " "
    def remains(self) -> str:
        return self._input

YY_reader = Reader()   # The historical prefix "YY_" is attached to make it global

def read_expr() -> Data:
    if YY_reader.LA() == "(":
        data = read_list()
        return data
    elif YY_reader.LA() == ")":
        raise SyntaxError
    elif YY_reader.LA() == "'":
        qlst = cons(mksym("인용"), cons(nil, nil))
        _ = YY_reader.next_token()
        data = read_expr()
        qdta = cdr(qlst)
        qdta.setcar(data)
        return qlst
    elif YY_reader.LA() == "`":
        qlst = cons(mksym("특이인용"), cons(nil, nil))
        _ = YY_reader.next_token()
        data = read_expr()
        qdta = cdr(qlst)
        qdta.setcar(data)
        return qlst
    elif YY_reader.LA() == ",@":
        qlst = cons(mksym("비인용연결"), cons(nil, nil))
        _ = YY_reader.next_token()
        data = read_expr()
        qdta = cdr(qlst)
        qdta.setcar(data)
        return qlst
    elif YY_reader.LA() == ",":
        qlst = cons(mksym("비인용"), cons(nil, nil))
        _ = YY_reader.next_token()
        data = read_expr()
        qdta = cdr(qlst)
        qdta.setcar(data)
        return qlst
    elif YY_reader.LA() == "":
        YY_reader.read2()
        _ = YY_reader.next_token()
        return read_expr()
    else:
        tok = YY_reader.LA()
        data = read_atom(tok)
        _ = YY_reader.next_token()
        return data
    # for test: return mkint(1910)

def read_atom(s: str) -> Data:
    """read an integer, nil, or a string"""
    if s.isdigit() or (len(s) > 1 and (s[0] == '+' or s[0] == '-')):
        return mkint(int(s))
    elif s == '공':
        return nil
    else:
        return mksym(s)         # 맞는 심볼만 검사 후 raise SyntaxError를 할 수도 있음

def read_list() -> Data:
    """read a list except the leading '('"""
    # YY_reader.match('(')          # 검사할 필요 없음
    YY_reader.nestin()
    YY_reader.next_token()
    result = nil
    if YY_reader.LA() == ')':
        YY_reader.nestout()
        return result
    fst = read_expr()  # retract tok and read an expression
    lst = cons(fst, nil)
    prev = lst
    while YY_reader.LA() != ')' and YY_reader.LA() != '.':
        elem = read_expr()    # using the lookahead
        last = cons(elem, nil)
        prev.setcdr(last)
        prev = last
    if YY_reader.LA() == '.':
        YY_reader.match('.')    #s1 = s2 였었나? YY_reader 도입 전에는 match('.')
        _ = YY_reader.next_token()
        elem = read_expr()
        prev.setcdr(elem)   # last.setcdr(elem)와 같음. 이 시점에서는 assert(_ == ')')
    YY_reader.nestout()
    YY_reader.match(')')
    YY_reader.next_token()
    return lst

def main_p():
    """test function for parsing"""
    while (_ := YY_reader.read()) != "":
        try:
            _ = YY_reader.next_token()
            expr = read_expr()
            print(expr)
        except SyntaxError:
            print("Syntax Error")

if __name__ == "__main__":
    main_p()
