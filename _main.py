#coding: utf-8

# Ph. 14: Multiline
#       YY_reader, YY_input 설정
#       read_expr 호출 전에 next_token으로 LA를 먼저 설정

from _data import *
from _parse import *
from _error import *
from _eval import *

def load_file(env: Data, path: str) -> None:
    global YY_reader
    print(f"Reading {path}...")
    YY_reader.readfile(path)
    tok = YY_reader.next_token()
    while YY_reader.remains() != "":
        try:
            expr = read_expr()
            result = eval(expr, env)
            print(result)
        except ErrLisp as err:
            print(f"ERROR: {err}")

def main():
    global YY_reader

    env = mkenv(nil)

    envset(env, mksym("머"), mkbuiltin(builtin_car))
    envset(env, mksym("꼬"), mkbuiltin(builtin_cdr))
    envset(env, mksym("짝"), mkbuiltin(builtin_cons))
    envset(env, mksym("+"), mkbuiltin(builtin_add))
    envset(env, mksym("-"), mkbuiltin(builtin_sub))
    envset(env, mksym("*"), mkbuiltin(builtin_mul))
    envset(env, mksym("/"), mkbuiltin(builtin_div))
    envset(env, mksym("#참"), mksym("#참"))
    envset(env, mksym("="), mkbuiltin(builtin_inteq))
    envset(env, mksym("<"), mkbuiltin(builtin_intlt))
    envset(env, mksym("적용"), mkbuiltin(builtin_apply))
    envset(env, mksym("같다?"), mkbuiltin(builtin_eq))
    envset(env, mksym("짝?"), mkbuiltin(builtin_ispair))
    envset(env, mksym("그리고"), mkbuiltin(builtin_and))
    envset(env, mksym("입력"), mkbuiltin(builtin_read))
    envset(env, mksym("출력"), mkbuiltin(builtin_write))

    load_file(env, "library_kor.scm")

    # reader = StdinReader()        # reader is set in _parse as global
    while (s := YY_reader.read()) != "":
        try:
            # print(f"BEFORE: {s}")
            tok = YY_reader.next_token()
            expr = read_expr()
            val = eval(expr, env)
            print(val)
            # print(f"AFTER:  {YY_reader.remains()}")
        except ErrLisp as err:
            print(f"오류: {err}")
        # except RunOutOfInput:
        #     print(f"'머꼬' 사용에 감사드립니다.")

if __name__ == "__main__":
    main()

"""
키워드: 정의(define), 람다(lambda), 만약(if), 인용(quote), 매크로(macro),
        특이인용(`), 비인용(,), 비인용연결(,@)
        # 비인용해제(unquote-splicing)
내장함수: 머(car), 꼬(cdr), 짝(cons), +, -, *, /, =, <, 입력(read), 출력(write)
내장 리터럴: 공(nil), #참(t)
"""

""" TEST Session for Ch 13
Reading library.lisp...
abs
foldl
foldr
list
reverse
unary-map
map
append
caar
cadr
quasiquote
> `(+ 1 ,(+ 2 3))
(+ 1 5)
> (define l `(3 4))
l
> l
(3 4)
> `(1 2 l)
(1 2 l)
> `(1 2 ,@l)
(1 2 3 4)
> `(1 2 ,@l 5)
(1 2 3 4 5)
>

> (let ((x 3) (y 5)) (+ x y))
8
> x
Error: Symbol not bound for 'x'
> (define + (let ((old+ +)) (lambda xs (foldl old+ 0 xs))))
+
> (+ 1 2 3 4)
10
>
"""