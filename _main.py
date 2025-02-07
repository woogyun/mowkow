#coding: utf-8

# Ph. 14: Multiline
#       YY_reader, YY_input 설정
#       read_expr 호출 전에 next_token으로 LA를 먼저 설정

import argparse

from _data import Data, nil, mksym, mkbuiltin
from _parse import YY_reader, Reader, read_expr
from _error import IsVerbose, eprint, ErrLisp
from _eval import mkenv, envset, eval, \
        builtin_car, builtin_cdr, builtin_cons, \
        builtin_add, builtin_sub, builtin_mul, builtin_div, \
        builtin_inteq, builtin_intlt, builtin_intgt, \
        builtin_apply, builtin_eq, builtin_ispair, builtin_isnil, builtin_not, builtin_and, builtin_or, \
        builtin_read, builtin_write, builtin_gensym 

def load_file(env: Data, path: str) -> None:
    #global YY_reader: Reader
    # global IsVerbose

    # if IsVerbose:
    #     eprint(f"'{path}'을(를) 불러오는 중입니다...")
    YY_reader.readfile(path)
    tok = YY_reader.next_token()
    while YY_reader.remains() != "":
        try:
            expr = read_expr()
            result = eval(expr, env)
            if result != None:
                eprint(result)
        except ErrLisp as err:
            eprint(f"오류: {err}")

def main():
    #global YY_reader: Reader
    # global IsVerbose

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
    envset(env, mksym(">"), mkbuiltin(builtin_intgt))
    envset(env, mksym("적용"), mkbuiltin(builtin_apply))
    envset(env, mksym("같다?"), mkbuiltin(builtin_eq))
    envset(env, mksym("짝?"), mkbuiltin(builtin_ispair))
    envset(env, mksym("공?"), mkbuiltin(builtin_isnil))
    envset(env, mksym("부정"), mkbuiltin(builtin_not))
    envset(env, mksym("그리고"), mkbuiltin(builtin_and))
    envset(env, mksym("또는"), mkbuiltin(builtin_or))
    envset(env, mksym("입력"), mkbuiltin(builtin_read))
    envset(env, mksym("출력"), mkbuiltin(builtin_write))
    envset(env, mksym("_모"), mkbuiltin(builtin_gensym))

    argparser = argparse.ArgumentParser()
    argparser.add_argument("files", nargs="*", help="소스 파일 목록")
    # argparser.add_argument("-v", "--verbose", help="상세 정보 출력")
    arg = argparser.parse_args()
    # if arg.verbose:
    #     IsVerbose = True

    load_file(env, "library_kor.scm")

    for file in arg.files:
        load_file(env, file)

    if not arg.files:
        # IsVerbose = True
        eval_print_loop(env)
    
def eval_print_loop(env: Data) -> None:
    while (_ := YY_reader.read()) != "":
        try:
            # print(f"BEFORE: {s}")
            _ = YY_reader.next_token()
            expr = read_expr()
            val = eval(expr, env)
            if val != None:
                print(val)
            # print(f"AFTER:  {YY_reader.remains()}")
        except ErrLisp as err:
            eprint(f"오류: {err}")
        except EOFError:
            eprint("'머꼬'를 사용해 주셔서 고맙습니다.")
            break
        # except RunOutOfInput:
        #     print(f"'머꼬' 사용에 감사드립니다.")

if __name__ == "__main__":
    main()

"""
키워드: 정의(define), 람다(lambda), 만약(if), 인용(quote), 매크로(macro),
        특이인용(`), 비인용(,), 비인용연결(,@), _모(gensym), 조건(cond), 잠시(let*)
        # 비인용해제(unquote-splicing)
내장함수:   
    머(car), 꼬(cdr), 짝(cons), 
    +, -, *, /, 
    =, <, 적용(apply), 같다?(eq), 짝?(pair?), 공?(nil?), 그리고(and),
    입력(read), 출력(write)
내장 리터럴: 공(nil), #참(t)
"""


""" TEST Session for Ph 15
D:\dev\mowkow>python _main.py
'library_kor.scm'을(를) 불러오는 중입니다...
머리
꼬리
머머
꼬머
그대로
아톰?
리스트?
절댓값
머리돌기
꼬리돌기
리스트
거꾸로
한맵
맵
접합
특이인용
임시
>  (조건 (#참 3))
3
>  (조건 ((< 3 2) 3) (#참 5))
5
>  (잠시
..   ((x 2)
..    (y (+ 1 x)))
..   (+ x y))
5
>  (잠시 ((x 3) (f (람다 (n) (만약 (= n 0) 1 (* n (f (- n 1))))))) (f x))
6
"""


""" TEST Session for Ph 13
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

""" 내장 함수 _모, 라이브러리 새함수 추가 후 테스트
\dev\mowkow>python _main.py
'library_kor.scm'을(를) 불러오는 중입니다...
머리
꼬리
머머
꼬머
그대로
아톰?
리스트?
절댓값
머리돌기
꼬리돌기
리스트
거꾸로
한맵
맵
접합
특이인용
임시
새함수
>  (새함수 (+ 2 3))
#기호2000
>  (#기호2000 1)
5
>  (#기호2000 100)
5
>
"""