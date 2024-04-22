#coding: utf-8

from _data import *
from _parse import *
from _error import *

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


# 내장 함수
#       car, cdr, cons,
#       add(+), sub(-), mul(*), div(/),
#       inteq(=), intlt(<)

def builtin_car(args: Data) -> Data:
    if not isunary(args):
        raise ErrArgs("머")
    if car(args).isnil():
        return nil              # 본래는 오류여야 함
    if not car(args).ispair():
        raise ErrType("머")
    return car(car(args))

def builtin_cdr(args: Data) -> Data:
    if not isunary(args):
        raise ErrArgs("꼬")
    if car(args).isnil():
        return nil              # 본래는 오류여야 함
    if not car(args).ispair():
        raise ErrType("꼬")
    return cdr(car(args))

def builtin_cons(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("짝")
    return cons(car(args), car(cdr(args)))

def builtin_add(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '+'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '+'>")
    return mkint(a.value() + b.value())

def builtin_sub(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '-'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '-'>")
    return mkint(a.value() - b.value())

def builtin_mul(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '*'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '*'>")
    return mkint(a.value() * b.value())

def builtin_div(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '/'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '/'>")
    return mkint(a.value() // b.value())

def builtin_inteq(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '='>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<내장함수 '='>")
    return mksym("#참") if a.value() == b.value() else nil

def builtin_intlt(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '<'>")
    a = car(args)
    b = car(cdr(args))
    if not a.isint() or not b.isint():
        raise ErrType("<builtin <>")
    return mksym("#참") if a.value() < b.value() else nil

def builtin_apply(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("적용")
    fn = car(args)
    args = car(cdr(args))
    if not islist(args):
        raise ErrSyntax("적용")
    return apply(fn, args)

def builtin_eq(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("같다?")
    a = car(args)
    b = car(cdr(args))
    if a.isnil() and b.isnil():
        eq = True
    elif a.issymbol() and b.issymbol():
        eq = a.value() == b.value()
    elif a.isint() and b.isint():
        eq = a.value() == b.value()
    elif a.isbuiltin() and b.isbuiltin():
        eq = a.fun() == b.fun()
    elif a.ispair() and b.ispair():
        eq = a.car() == b.car() and a.cdr() == b.cdr()
    elif a.isclosure() and b.isclosure():
        eq = a.val() == b.val()
    elif a.ismacro() and b.ismacro():
        eq = a.val() == b.val()
    else:
        eq = False
    return mksym("#참") if eq else nil

def builtin_ispair(args: Data) -> Data:
    if not isunary(args):
        raise ErrArgs("<내장함수 '짝?'>")
    return mksym("#참") if car(args).ispair() else nil

def builtin_isnil(args: Data) -> Data:
    if not isunary(args):
        raise ErrArgs("<내장함수 '공?'>")
    return mksym("#참") if car(args).isnil() else nil

def builtin_not(args: Data) -> Data:
    if not isunary(args):
        raise ErrArgs("<내장함수 '부정'>")
    return mksym("#참") if car(args).isnil() else nil

def builtin_and(args: Data) -> Data:
    if not isbinary(args):
        raise ErrArgs("<내장함수 '그리고'>")
    a = car(args)
    b = car(cdr(args))
    if a.issymbol() and a.value() == "#참":
        return b
    elif a.isnil():
        return nil
    else:
        raise ErrType("<내장함수 '그리고'>")

def builtin_read(args: Data) -> Data:
    fname = "입력"
    if not isvoid(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    line = input("")
    if line.isdigit():
        return mkint(int(line))
    elif line.isalpha():
        return mksym(line)
    else:
        raise ErrType(f"<내장함수 '{fname}'>")

def builtin_write(args: Data) -> Data:
    fname = "출력"
    if not isunary(args):
        raise ErrArgs(f"<내장함수 '{fname}'>")
    a = car(args)
    if a.issymbol() or a.isint() or a.isnil():
        print(a.value())
        return mksym("#참")
    elif a.isbuiltin():
        print(f"<내장함수>")
        return mksym("#참")
    elif a.ispair():
        print(f"{a}")


# 환경
#   mkenv(parent): 부모 환경이 parent인 환경을 만든다.
#   envget(env, symbol): 환경 env에서 이름 symbol을 찾는다.
#               없으면 ErrUnbound 발생
#   envset(env, symbol, value): 환경에 symbol = value를 추가한다.

def mkenv(parent: Data) -> Data:
    env = cons(parent, nil)
    return env

def envget(env: Data, symbol: Data) -> Data:
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
    binds = cdr(env)
    while not binds.isnil():
        bind = car(binds)
        if car(bind).value() == symbol.value():
            bind.setcdr(value)              # modify the entry found
            return
        binds = cdr(binds)
    bind = cons(symbol, value)              # new entry
    env.setcdr(cons(bind, cdr(env)))        # prepend a new entry

def eval(expr: Data, env: Data) -> Data:
    if expr.issymbol():
        return envget(env, expr)
    if not expr.ispair():
        return expr
    if not islist(expr):
        raise ErrSyntax()
    fun  = car(expr)
    args = cdr(expr)
    if fun.issymbol():  # bug_230104e: keyword parts are guarded
        if fun.value() == "인용":
            if not isunary(args):
                raise ErrArgs("인용")
            return car(args)
        if fun.value() == "정의":
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
                val = eval(exp, env)
            else: # not sym.issymbol():
                raise ErrType("정의")
            envset(env, sym, val)
            return sym
        if fun.value() == "람다":
            if not isbinary(args):
                raise ErrArgs("람다")
            return mkclosure(env, car(args), cdr(args))
        if fun.value() == "만약":
            if not isternary(args):
                raise ErrArgs("만약")
            cond = eval(car(args), env)
            tval = car(cdr(args))
            fval = car(cdr(cdr(args)))
            val = fval if cond.isnil() else tval
            return eval(val, env)
        if fun.value() == "매크로":
            if not isbinary(args):
                raise ErrArgs("매크로")
            if not car(args).ispair():
                raise ErrSyntax("매크로")
            name = car(car(args))
            if not name.issymbol():
                raise ErrType("매크로")
            macro = mkmacro(env, cdr(car(args)), cdr(args))
            envset(env, name, macro)
            return name

    # builtin functions, lambda, and macro

    # Evaluate operator
    fn = eval(fun, env)     # eval the function part

    if fn.ismacro():        # if the function is a macro
        mval = fn.val()
        menv = car(mval)
        mparams = car(cdr(mval))
        mbody = cdr(cdr(mval))
        newfn = mkclosure(menv, mparams, mbody)
        expansion = apply(newfn, args)
        return eval(expansion, env)

    # Evaluate arguments
    args = cplist(args)     # copy the argument list
    p = args
    while not p.isnil():
        p.setcar(eval(car(p), env))
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
            raise ErrArgs()
        envset(env, car(params), car(args))
        params = cdr(params)
        args = cdr(args)
    if not args.isnil():
        raise ErrArgs()
    while not body.isnil():     # q_230102: 왜 body를 계속 계산하나? 수식 하나 아닌가?
        result = eval(car(body), env)
        body = cdr(body)
    return result

def main_e():
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
    envset(env, mksym("부정"), mkbuiltin(builtin_not))
    envset(env, mksym("입력"), mkbuiltin(builtin_read))
    envset(env, mksym("출력"), mkbuiltin(builtin_write))

    while (s := input("> ")) != "":
        try:
            expr, s = read_expr(s)
            val = eval(expr, env)
            print(val)
            #print(s)
        except ErrLisp as err:
            print(f"Error: {err}")

if __name__ == "__main__":
    main_e()

"""
키워드:     정의(define), 람다(lambda), 만약(if), 인용(quote), 매크로(macro),
            특이인용(`), 비인용(,), 비인용연결(,@)
            # 비인용해제(unquote-splicing)
내장함수:   머(car), 꼬(cdr), 짝(cons), 
            +, -, *, /, 
            짝?(pair?), 공?(nil?), =, <, 부정(not), 
            입력(read), 출력(write)
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