#coding: utf-8

from _data import *
from _parse import *
from _error import IsVerbose, eprint, ErrLisp, ErrSyntax, ErrUnbound, ErrArgs, ErrType

# Ph 8
#       global isternary(Data): 인수 개수가 3개인지 검사
#       eval의 fun.issymbol() 블록에 "if" 처리 추가
#       main의 envset(env, mksym("#t"), mksym("#t")) 추가
#       내장 함수 builtin_inteq, builtin_intlt 추가
#       main에서 envset에서 (= . builtin_inteq), (< . builtin_intlt) 추가

# Ph 9
#       eval: define 키워드 처리 시 sym이 pair인 경우(sym.ispair()) 처리 추가
#             이로 인해서 sym이 symbol인 경우의 코드를 재구성함
#             인수가 없는 람다도 가능한가? -> 가능함(테스트 세션 3 참고)

# Ph 10. Variadic
#       apply: parameter가 이름(symbol)인 경우 나머지 인수에 바인딩하는 코드 추가

# Ph 11. Macro
#       eval: defmacro 섹션 추가

# Ph 12. Library
#       builtin_apply(Data)
#       builtin_eq(Data)
#       builtin_ispair(Data)

# Ph 15. 조건(cond) 및 잠시(let*) 처리
#       eval: 조건(cond) 및 잠시(let*) 처리 추가
#             조건(cond)은 조건이 참인 경우에만 계산하고 하나도 참이 아니면 nil을 반환함
#             잠시(let*)은 바인딩을 순차적으로 처리함(let은 병렬 처리임에 반해 let*은 순차 처리임)

# 내장 함수
#       car, cdr, cons,
#       add(+), sub(-), mul(*), div(/),
#       inteq(=), intlt(<)


def builtin_gensym(args: Data, _gensym_counter: int=20000) -> Data:
    '''새 기호를 만들어서 반환한다. 인수는 없어야 한다.'''
    fname = "_모"       # 새 기호를 만들어서 반환(_새글)
    if not isvoid(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    name = "#기호" + str(_gensym_counter)
    _gensym_counter += 1
    return mksym(name)

def builtin_car(args: Data) -> Data:
    '''머리 함수: (car (a b)) -> a'''
    if not isunary(args):
        raise ErrArgs("머")
    if car(args).isnil():
        return nil              # 본래는 오류여야 함
    if not car(args).ispair():
        raise ErrType("머")
    return car(car(args))

def builtin_cdr(args: Data) -> Data:
    '''꼬리 함수: (cdr (a b)) -> b'''
    if not isunary(args):
        raise ErrArgs("꼬")
    if car(args).isnil():
        return nil              # 본래는 오류여야 함
    if not car(args).ispair():
        raise ErrType("꼬")
    return cdr(car(args))

def builtin_cons(args: Data) -> Data:
    '''짝 함수: (cons a b) -> (a . b)'''
    if not isbinary(args):
        raise ErrArgs("짝")
    return cons(car(args), car(cdr(args)))

def builtin_add(args: Data) -> Data:
    '''덧셈 함수: (+ 1 2) -> 3'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '+'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '+'>")
    return mkint(a.value() + b.value())

def builtin_sub(args: Data) -> Data:
    '''뺄셈 함수: (- 3 2) -> 1'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '-'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '-'>")
    return mkint(a.value() - b.value())

def builtin_mul(args: Data) -> Data:
    '''곱셈 함수: (* 2 3) -> 6'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '*'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '*'>")
    return mkint(a.value() * b.value())

def builtin_div(args: Data) -> Data:
    '''나눗셈 함수: (/ 6 3) -> 2'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '/'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '/'>")
    return mkint(a.value() // b.value())

def builtin_inteq(args: Data) -> Data:
    '''정수 같다 함수: (= 1 1) -> #참'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '='>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '='>")
    return mksym("#참") if a.value() == b.value() else nil

def builtin_intlt(args: Data) -> Data:
    '''정수 작다 함수: (< 1 2) -> #참'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '<'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '<'>")
    return mksym("#참") if a.value() < b.value() else nil

def builtin_intgt(args: Data) -> Data:
    '''정수 크다 함수: (> 1 2) -> 공'''
    if not isbinary(args):
        raise ErrArgs("<내장함수 '>'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '>'>")
    return mksym("#참") if a.value() > b.value() else nil

def builtin_apply(args: Data) -> Data:
    '''함수 적용 함수: (apply fn args) -> (fn . args)'''
    if not isbinary(args):
        raise ErrArgs("적용")
    fn = car(args)
    args = car(cdr(args))
    if not islist(args):
        raise ErrSyntax()
    return apply(fn, args)

def builtin_eq(args: Data) -> Data:
    '''같다? 함수: (eq a b) -> #참'''
    if not isbinary(args):
        raise ErrArgs("같다?")
    a, b = car(args), car(cdr(args))
    if a.isnil() and b.isnil():
        eq = True
    elif a.issymbol() and b.issymbol() or a.isint() and b.isint():
        eq = a.value() == b.value()
    elif a.isbuiltin() and b.isbuiltin():
        eq = a.fun() == b.fun()
    elif a.ispair() and b.ispair():
        eq = a.car() == b.car() and a.cdr() == b.cdr()
    elif a.isclosure() and b.isclosure() or a.ismacro() and b.ismacro():
        eq = a.val() == b.val()
    else:
        eq = False
    return mksym("#참") if eq else nil

def builtin_ispair(args: Data) -> Data:
    '''짝? 함수: (짝? (a b)) -> #참'''
    if not isunary(args):
        raise ErrArgs("<내장함수 '짝?'>")
    return mksym("#참") if car(args).ispair() else nil

def builtin_isnil(args: Data) -> Data:
    '''공? 함수: (공? (a b)) -> #참'''
    if not isunary(args):
        raise ErrArgs("<내장함수 '공?'>")
    return mksym("#참") if car(args).isnil() else nil

def builtin_not(args: Data) -> Data:
    '''부정 함수: (부정 #참) -> 공'''       # (부정 #참) -> 공, (부정 공) -> #참 (cf. 반 for 반대)
    if not isunary(args):
        raise ErrArgs("<내장함수 '부정'>")
    return mksym("#참") if car(args).isnil() else nil

def builtin_and(args: Data) -> Data:
    '''그리고 함수: (그리고 #참 #참) -> #참'''     # (그리고 #참 #참) -> #참, (그리고 #참 공) -> 공 (cf. 다 for 모두다)
    fname = "그리고"
    if not isbinary(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    a = car(args)
    b = car(cdr(args))
    if a.issymbol() and a.value() == "#참":
        return b
    elif a.isnil():
        return nil
    else:
        raise ErrType("<내장함수 '{fname}'>")

def builtin_or(args: Data) -> Data:
    '''또는 함수: (또는 #참 공) -> #참'''       # (또는 #참 공) -> #참, (또는 공 공) -> 공 (cf. 또 for 혹)
    fname = "또는"      # 혹
    if not isbinary(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    a = car(args)
    b = car(cdr(args))
    if a.isnil():
        return b
    else:
        return a
    # elif a.issymbol() and a.value() == "#참":
    #     return a
    # else:
    #     raise ErrType("<내장함수 '{fname}'>")

def builtin_read(args: Data) -> Data:
    '''입력 함수: (읽기) -> 123'''     # (읽기) -> 123 (cf. 입력)
    fname = "읽기"
    if not isvoid(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    line = input("").strip()
    if line.isdigit():
        return mkint(int(line))
    elif line.isalpha():
        return mksym(line)
    elif line[0] == line[-1] == '"':    # "문자열"
        return mkstr(line)
    else:
        raise ErrType(f"<내장함수 '{fname}'>")

def builtin_write(args: Data, terminator="\n") -> None:
    '''출력 함수: (쓰기 123) -> 123'''     # (쓰기 123) -> 123 (cf. 출력)
    fname = "출력"
    if not isunary(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    a = car(args)
    if a.issymbol() or a.isint() or a.ispair() or a.isbuiltin():
        print(a, end=terminator)
    elif a.isstr():
        print(a.__str__(), end="")
    elif a.isnil():
        print("()", end=terminator)

# 환경
#   mkenv(parent): 부모 환경이 parent인 환경을 만든다.
#   envget(env, symbol): 환경 env에서 이름 symbol을 찾는다.
#               없으면 ErrUnbound 발생
#   envset(env, symbol, value): 환경에 symbol = value를 추가한다.

def mkenv(parent: Data) -> Data:
    '''부모 환경이 parent인 환경을 만든다.'''
    env = cons(parent, nil)
    return env

def envget(env: Data, symbol: Data) -> Data:
    '''환경 env에서 이름 symbol을 찾는다. 없으면 ErrUnbound 발생'''
    parent = env.car()
    binds  = env.cdr()
    while not binds.isnil():
        bind = car(binds)
        if car(bind).value() == symbol.value():
            return cdr(bind)
        binds = cdr(binds)
    if parent.isnil():
        raise ErrUnbound(symbol.value())
    return envget(parent, symbol)        

def envset(env: Data, symbol: Data, value: Data) -> None:
    '''환경에 symbol = value를 추가한다.'''
    binds = cdr(env)
    while not binds.isnil():
        bind = car(binds)
        if car(bind).value() == symbol.value():
            bind.setcdr(value)              # modify the entry found
            return
        binds = cdr(binds)
    bind = cons(symbol, value)              # new entry
    env.setcdr(cons(bind, cdr(env)))        # prepend a new entry

def mk_eval(expr: Data, env: Data) -> Data:
    '''수식 expr을 환경 env에서 계산한다.'''
    if expr.issymbol():
        return envget(env, expr)
    if not expr.ispair():
        return expr
    if not islist(expr):    # 순차 수식은 허용하지 않음
        raise ErrSyntax()
    fun  = car(expr)
    args = cdr(expr)
    if fun.issymbol():      # bug_230104e: keyword parts are guarded
        if fun.value() == "인용":       # 키워드 '인용'(quote) 처리: (인용 exp)
            if not isunary(args):
                raise ErrArgs("인용")
            return car(args)
        if fun.value() == "정의":       # 키워드 '정의'(define) 처리: (정의 sym exp)
            if not isbinary(args):
                raise ErrArgs("정의")
            sym = car(args)
            if sym.ispair():
                val = mkclosure(env, cdr(sym), cdr(args))
                sym = car(sym)
                if not sym.issymbol():
                    raise ErrType("정의")
            elif sym.issymbol():
                ## Duplication for not isbianry(args) is true.
                # if not cdr(cdr(args)).isnil():
                #     raise ErrArgs("define")
                exp = car(cdr(args))
                val = mk_eval(exp, env)
            else: # not sym.issymbol():
                raise ErrType("정의")
            envset(env, sym, val)
            if IsVerbose:
                eprint(sym)
            return None
        if fun.value() == "람다":       # 키워드 '람다'(lambda) 처리: (람다 (params) body)
            if not isbinary(args):
                raise ErrArgs("람다")
            return mkclosure(env, car(args), cdr(args))
        if fun.value() == "만약":       # 키워드 '만약'(if) 처리: (만약 cond tval fval)
            if not isternary(args):
                raise ErrArgs("만약")
            cond = mk_eval(car(args), env)
            tval = car(cdr(args))
            fval = car(cdr(cdr(args)))
            val = fval if cond.isnil() else tval
            return mk_eval(val, env)
        if fun.value() == "조건":       # 키워드 '조건'(cond) 처리: (조건 (cond1 val1) (cond2 val2) ...)
            if isvoid(args):
                raise ErrArgs("조건")
            while not args.isnil():
                clause = car(args)
                if not clause.ispair():
                    raise ErrSyntax()
                if not cdr(clause).ispair():
                    raise ErrSyntax()
                cond = mk_eval(car(clause), env)
                val = car(cdr(clause))
                if not cond.isnil():
                    return mk_eval(val, env)
                args = cdr(args)
            return nil
        if fun.value() == "매크로":     # 키워드 '매크로'(defmacro) 처리: (매크로 (name params) body)
            if not isbinary(args):
                raise ErrArgs("매크로")
            if not car(args).ispair():
                raise ErrSyntax()
            name = car(car(args))
            if not name.issymbol():
                raise ErrType("매크로")
            macro = mkmacro(env, cdr(car(args)), cdr(args))
            envset(env, name, macro)
            if IsVerbose:
                eprint(name)
            return None
        if fun.value() == "잠시":       # 키워드 '잠시'(let) 처리 (잠시 ((name val) ...) body)
            if not isbinary(args):
                raise ErrArgs("잠시")
            bnds = car(args)
            body = car(cdr(args))
            local_env = mkenv(env)
            while not bnds.isnil():
                if not car(bnds).ispair():
                    raise ErrSyntax()
                abnd = car(bnds)
                if not abnd.ispair():           # '잠시'의 한 바인딩이 pair가 아닌 경우
                    raise ErrType("잠시")
                if not car(abnd).issymbol():    # '잠시'의 한 바인딩의 이름이 symbol이 아닌 경우
                    raise ErrType("잠시")
                sym = car(abnd)
                val = mk_eval(car(cdr(abnd)), local_env)   # '잠시'의 한 바인딩의 값 계산(let*로 처리)
                envset(local_env, sym, val)             # '잠시'의 한 바인딩을 환경 local_env에 추가
                bnds = cdr(bnds)
            val = mk_eval(body, local_env)                 # '잠시'의 body 계산
            # env는 그대로이므로 local_env를 삭제하고 회복하는 과정이 필요 없음
            return val

    # builtin functions, lambda, and macro

    # Evaluate operator
    fn = mk_eval(fun, env)     # eval the function part

    if fn.ismacro():        # if the function is a macro
        mval = fn.val()
        menv = car(mval)
        mparams = car(cdr(mval))
        mbody = cdr(cdr(mval))
        newfn = mkclosure(menv, mparams, mbody)
        expansion = apply(newfn, args)
        return mk_eval(expansion, env)

    # Evaluate arguments
    args = cplist(args)     # copy the argument list
    p = args
    while not p.isnil():
        p.setcar(mk_eval(car(p), env))
        p = cdr(p)
    return apply(fn, args)
    # if not fun.issymbol():      
        # raise ErrSyntax()

def isvoid(args):
    return args.isnil()

def isunary(args):
    return not args.isnil() and cdr(args).isnil()

def isbinary(args):
    return not args.isnil() and not cdr(args).isnil() and cdr(cdr(args)).isnil()

def isternary(args):
    return not args.isnil() and not cdr(args).isnil() and not cdr(cdr(args)).isnil() and cdr(cdr(cdr(args))).isnil()

def apply(fn: Data, args: Data) -> Data:
    if fn.isbuiltin():
        return fn.fun()(args)
    if not fn.isclosure():
        raise ErrType("<#클로저>")
    env = mkenv(fn.env())       # bug_230104b: mkenv(car(fn)) -> mkenv(fn.env())
    params = fn.params()        # bug_230104c: car(cdr(fn))   -> fn.params()
    body = fn.body()            # bug_230104d: cdr(cdr(fn))   -> fn.body()
    while not params.isnil():
        if params.issymbol():   # for the variadic parameter (ch 10)
            envset(env, params, args)
            args = nil
            break
        if args.isnil():        # for normal parameters
            raise ErrArgs("<#클로저>")
        envset(env, car(params), car(args))
        params = cdr(params)
        args = cdr(args)
    if not args.isnil():
        raise ErrArgs("<#클로저>")
    while not body.isnil():     # q_230102: 왜 body를 계속 계산하나? 수식 하나 아닌가?
        result = mk_eval(car(body), env)
        body = cdr(body)
    return result

def _main_e():
    env = mkenv(nil)

    envset(env, mksym("머"), mkbuiltin(builtin_car))
    envset(env, mksym("꼬"), mkbuiltin(builtin_cdr))
    envset(env, mksym("짝"), mkbuiltin(builtin_cons))
    envset(env, mksym("+"), mkbuiltin(builtin_add))
    envset(env, mksym("-"), mkbuiltin(builtin_sub))
    envset(env, mksym("*"), mkbuiltin(builtin_mul))
    envset(env, mksym("/"), mkbuiltin(builtin_div))
    envset(env, mksym("#참"), mksym("#참"))
    envset(env, mksym("짝?"), mkbuiltin(builtin_ispair))
    envset(env, mksym("="), mkbuiltin(builtin_inteq))
    envset(env, mksym("<"), mkbuiltin(builtin_intlt))
    envset(env, mksym(">"), mkbuiltin(builtin_intgt))
    envset(env, mksym("부정"), mkbuiltin(builtin_not))
    envset(env, mksym("읽기"), mkbuiltin(builtin_read))
    envset(env, mksym("쓰기"), mkbuiltin(builtin_write))
    # envset(env, mksym("_새글"), mkbuiltin(builtin_gensym))

    # load_file(env, "library_kor.scm")
    global YY_reader
    while (s := YY_reader.read()) != "":
        try:
            # print(f"BEFORE: {s}")
            tok = YY_reader.next_token()
            expr = read_expr()
            val = mk_eval(expr, env)
            if val != None:
                print(val)
            # print(f"AFTER:  {YY_reader.remains()}")
        except ErrLisp as err:
            eprint(f"오류: {err}")
    # while (s := input("> ")) != "":
    #     try:
    #         expr, s = read_expr(s)
    #         val = eval(expr, env)
    #         print(val)
    #         #print(s)
    #     except ErrLisp as err:
    #         print(f"Error: {err}")

if __name__ == "__main__":
    _main_e()

"""
키워드:     정의(define), 람다(lambda), 만약(if), 인용(quote), 매크로(macro),
            특이인용(`), 비인용(,), 비인용연결(,@), _모(gensym), 조건(cond), 잠시(let*)
            # 비인용해제(unquote-splicing)
내장함수:   머(car), 꼬(cdr), 짝(cons), 
            +, -, *, /, 
            짝?(pair?), 공?(nil?), =, <, 부정(not), 
            읽기(read), 쓰기(write)
내장 리터럴: 공(nil), #참(t)
"""

"""TEST Session for Ch 12
> (defmacro (ignore x) (cons 'quote (cons x nil)))
ignore
> (ignore foo)
foo
> foo
Error: Symbol not bound for 'foo'
>
"""