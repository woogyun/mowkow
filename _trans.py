#coding: utf-8
"""머꼬(.mk) 소스를 교육용으로 읽기 좋은 Python 코드로 번역하는 모듈."""

import keyword
from _data import Data
from _parse import parse_string

PREC_LOWEST  = 0
PREC_LAMBDA  = 1
PREC_TERNARY = 2
PREC_OR      = 3
PREC_AND     = 4
PREC_NOT     = 5
PREC_CMP     = 6
PREC_ADD     = 7
PREC_MUL     = 8
PREC_UNARY   = 9
PREC_PRIMARY = 10

# 머꼬 심볼 -> (파이썬 연산자, 우선순위)
BINOPS = {
    "+": ("+", PREC_ADD),  "-": ("-", PREC_ADD),
    "*": ("*", PREC_MUL),  "/": ("//", PREC_MUL),
    "=": ("==", PREC_CMP), "<": ("<", PREC_CMP), ">": (">", PREC_CMP),
    "그리고": ("and", PREC_AND), "&": ("and", PREC_AND),
    "또는": ("or", PREC_OR),   "|": ("or", PREC_OR),
}

KEYWORDS = {"정의", "람다", "만약", "조건", "잠시", "해", "인용",
            "매크로", "특이인용", "비인용", "비인용연결"}


class TransUnsupported(Exception):
    """번역할 수 없는 구문을 만났을 때 발생. line 속성에 소스 행 번호."""
    def __init__(self, message, line=None):
        super().__init__(message)
        self.line = line


def sanitize(name: str) -> str:
    """특수 문자를 Python 식별자로 유효하게 치환(문자 수준, 중복 제거 없음)."""
    res = name.replace("->", "_로_").replace("=>", "_로_")
    res = res.replace("?", "_물음").replace("!", "_느낌").replace("-", "_")
    res = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in res)
    if res and res[0].isdigit():
        res = "_" + res
    if keyword.iskeyword(res):
        res = res + "_"
    return res


def to_list(d: Data) -> list:
    """머꼬 리스트를 Data 원소들의 파이썬 리스트로 변환. 점쌍이면 오류."""
    out = []
    while d.ispair():
        out.append(d.car())
        d = d.cdr()
    if not d.isnil():
        raise TransUnsupported("점쌍(dotted pair)은 지원하지 않습니다.",
                               getattr(d, "line", None))
    return out


def indent(lines, n=1):
    pad = "    " * n
    return [pad + ln if ln else ln for ln in lines]


def python_str_literal(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


class Transpiler:
    def __init__(self, src_name="<소스>"):
        self.src_name = src_name
        self.names = {}            # 원본 이름 -> 최종 파이썬 이름
        self.needs_functools = False

    def mangle(self, name: str) -> str:
        if name in self.names:
            return self.names[name]
        base = sanitize(name)
        final = base
        existing = set(self.names.values())
        i = 2
        while final in existing:
            final = f"{base}_{i}"
            i += 1
        self.names[name] = final
        return final

    def wrap(self, text, myprec, prec):
        return f"({text})" if myprec < prec else text

    def emit_expr(self, expr, prec):
        if expr.isnil():
            return "[]"
        if expr.isint():
            return str(expr.value())
        if expr.isstr():
            return expr.value()            # 저장된 값이 이미 따옴표 포함
        if expr.issymbol():
            v = expr.value()
            if v == "#참":
                return "True"
            return self.mangle(v)
        if expr.ispair():
            return self.emit_compound_expr(expr, prec)
        raise TransUnsupported("번역할 수 없는 식입니다.", getattr(expr, "line", None))

    def emit_quote(self, d):
        if d.isnil():
            return "[]"
        if d.isint():
            return str(d.value())
        if d.isstr():
            return d.value()
        if d.issymbol():
            return python_str_literal(d.value())
        if d.ispair():
            elems = [self.emit_quote(e) for e in to_list(d)]
            return "[" + ", ".join(elems) + "]"
        raise TransUnsupported("인용할 수 없는 값입니다.", getattr(d, "line", None))

    def emit_compound_expr(self, expr, prec):
        head = expr.car()
        args = to_list(expr.cdr())
        if head.issymbol():
            name = head.value()
            if name == "인용":
                return self.emit_quote(args[0])
            if name == "만약":
                return self.emit_if_expr(args, prec)
            if name == "람다":
                return self.emit_lambda(args, prec)
            if name == "잠시":
                return self.emit_let_expr_form(args, prec)
            if name in ("부정", "~"):
                inner = self.emit_expr(args[0], PREC_NOT)
                return self.wrap(f"not {inner}", PREC_NOT, prec)
            if name in BINOPS:
                return self.emit_binop(name, args, prec)
            if name in ("정의", "조건", "해", "매크로"):
                raise TransUnsupported(f"'{name}'은 식 문맥에서 번역할 수 없습니다.",
                                       getattr(expr, "line", None))
            if name in ("특이인용", "비인용", "비인용연결"):
                raise TransUnsupported(f"'{name}'(quasiquote 계열)은 v1에서 지원하지 않습니다.",
                                       getattr(expr, "line", None))
            builtin = self.emit_builtin_call(name, args, prec)
            if builtin is not None:
                return builtin
        return self.emit_call(head, args, prec)

    def emit_binop(self, name, args, prec):
        if len(args) != 2:
            raise TransUnsupported(f"'{name}'는 두 개의 인수가 필요합니다.", None)
        pyop, myprec = BINOPS[name]
        left = self.emit_expr(args[0], myprec)
        right = self.emit_expr(args[1], myprec + 1)  # 좌결합: 오른쪽은 한 단계 높게
        return self.wrap(f"{left} {pyop} {right}", myprec, prec)

    def emit_call(self, head, args, prec):
        fexpr = self.emit_expr(head, PREC_PRIMARY)
        argtext = ", ".join(self.emit_expr(a, PREC_LOWEST) for a in args)
        return f"{fexpr}({argtext})"

    def emit_builtin_call(self, name, args, prec):
        n = len(args)

        def E(i, p=PREC_LOWEST):
            return self.emit_expr(args[i], p)

        if name in ("머", "머리") and n == 1:
            return f"{self.emit_expr(args[0], PREC_PRIMARY)}[0]"
        if name in ("꼬", "꼬리") and n == 1:
            return f"{self.emit_expr(args[0], PREC_PRIMARY)}[1:]"
        if name == "머머" and n == 1:
            return f"{self.emit_expr(args[0], PREC_PRIMARY)}[0][0]"
        if name == "꼬머" and n == 1:
            return f"{self.emit_expr(args[0], PREC_PRIMARY)}[1]"
        if name == "짝" and n == 2:
            return self.wrap(f"[{E(0)}] + {self.emit_expr(args[1], PREC_ADD + 1)}",
                             PREC_ADD, prec)
        if name in ("리스트", "열"):
            return "[" + ", ".join(E(i) for i in range(n)) + "]"
        if name == "절댓값" and n == 1:
            return f"abs({E(0)})"
        if name == "거꾸로" and n == 1:
            return f"{self.emit_expr(args[0], PREC_PRIMARY)}[::-1]"
        if name == "접합" and n == 2:
            return self.wrap(f"{self.emit_expr(args[0], PREC_ADD)} + "
                             f"{self.emit_expr(args[1], PREC_ADD + 1)}", PREC_ADD, prec)
        if name == "그대로" and n == 1:
            return self.emit_expr(args[0], prec)
        if name in ("아톰?", "단?") and n == 1:
            return self.wrap(f"not isinstance({E(0)}, list)", PREC_NOT, prec)
        if name in ("리스트?", "열?") and n == 1:
            return f"isinstance({E(0)}, list)"
        if name == "공?" and n == 1:
            return self.wrap(f"{self.emit_expr(args[0], PREC_CMP)} == []", PREC_CMP, prec)
        if name == "짝?" and n == 1:
            inner = E(0)
            return self.wrap(f"isinstance({inner}, list) and {inner} != []",
                             PREC_AND, prec)
        if name == "같다?" and n == 2:
            return self.wrap(f"{self.emit_expr(args[0], PREC_CMP)} == "
                             f"{self.emit_expr(args[1], PREC_CMP + 1)}", PREC_CMP, prec)
        if name == "읽기" and n == 0:
            return "int(input())"
        if name == "쓰기" and n == 1:
            return f"print({E(0)})"
        if name == "한맵" and n == 2:
            return f"[{self.emit_expr(args[0], PREC_PRIMARY)}(e) for e in {E(1)}]"
        if name == "맵" and n == 2:
            return f"[{self.emit_expr(args[0], PREC_PRIMARY)}(e) for e in {E(1)}]"
        if name == "맵" and n >= 3:
            proc = self.emit_expr(args[0], PREC_PRIMARY)
            lists = ", ".join(E(i) for i in range(1, n))
            return f"list(map({proc}, {lists}))"
        if name in ("머리돌기", "꼬리돌기") and n == 3:
            self.needs_functools = True
            proc = self.emit_expr(args[0], PREC_PRIMARY)
            init, xs = E(1), E(2)
            if name == "머리돌기":
                return f"functools.reduce({proc}, {xs}, {init})"
            return f"functools.reduce(lambda a, b: {proc}(b, a), reversed({xs}), {init})"
        KNOWN_LIB = {"머", "꼬", "머리", "꼬리", "머머", "꼬머", "짝", "리스트", "열",
                     "절댓값", "거꾸로", "접합", "그대로", "아톰?", "단?", "리스트?", "열?",
                     "공?", "짝?", "같다?", "읽기", "쓰기", "한맵", "맵", "머리돌기", "꼬리돌기"}
        if name in KNOWN_LIB:
            raise TransUnsupported(f"'{name}' 호출의 인수 개수가 맞지 않습니다.", None)
        return None

    def param_names(self, params):
        names, p = [], params
        while p.ispair():
            names.append(self.mangle(p.car().value()))
            p = p.cdr()
        if p.issymbol():                       # 가변 인수 꼬리
            names.append("*" + self.mangle(p.value()))
        return names

    def emit_if_expr(self, args, prec):
        cond = self.emit_expr(args[0], PREC_TERNARY + 1)
        tval = self.emit_expr(args[1], PREC_TERNARY + 1)
        fval = self.emit_expr(args[2], PREC_TERNARY)
        return self.wrap(f"{tval} if {cond} else {fval}", PREC_TERNARY, prec)

    def emit_lambda(self, args, prec):
        params = self.param_names(args[0])
        body = args[1:]
        if len(body) != 1:
            raise TransUnsupported("본문이 여러 식인 람다는 식 문맥에서 지원하지 않습니다.", None)
        text = f"lambda {', '.join(params)}: {self.emit_expr(body[0], PREC_LAMBDA)}"
        return self.wrap(text, PREC_LAMBDA, prec)

    def emit_let_expr_form(self, args, prec):
        bindings = [(b.car(), b.cdr().car()) for b in to_list(args[0])]
        return self.emit_let_expr(bindings, args[1], prec)

    def emit_let_expr(self, bindings, body, prec):
        if not bindings:
            return self.emit_expr(body, prec)
        var, val = bindings[0]
        vname = self.mangle(var.value())
        inner = self.emit_let_expr(bindings[1:], body, PREC_LOWEST)
        vexpr = self.emit_expr(val, PREC_LOWEST)
        return f"(lambda {vname}: {inner})({vexpr})"

    def emit_stmt(self, expr, want_return):
        if expr.ispair() and expr.car().issymbol():
            name = expr.car().value()
            args = to_list(expr.cdr())
            if name == "만약":
                return self.emit_if_stmt(args, want_return)
            if name == "조건":
                return self.emit_cond_stmt(args, want_return)
            if name == "잠시":
                return self.emit_let_stmt(args, want_return)
            if name == "해":
                return self.emit_do_stmt(args, want_return)
            if name == "정의":
                return self.emit_define(args, toplevel=False)
            if name == "쓰기" and len(args) == 1:
                lines = [f"print({self.emit_expr(args[0], PREC_LOWEST)})"]
                if want_return:
                    lines.append("return None")
                return lines
        text = self.emit_expr(expr, PREC_LOWEST)
        return [f"return {text}"] if want_return else [text]

    def emit_if_stmt(self, args, want_return):
        cond = self.emit_expr(args[0], PREC_LOWEST)
        lines = [f"if {cond}:"]
        lines += indent(self.emit_stmt(args[1], want_return))
        lines += ["else:"]
        lines += indent(self.emit_stmt(args[2], want_return))
        return lines

    def emit_cond_stmt(self, clauses, want_return):
        lines, first = [], True
        for clause in clauses:
            parts = to_list(clause)
            test, body = parts[0], parts[1]
            if test.issymbol() and test.value() == "#참":
                lines.append("else:")
                lines += indent(self.emit_stmt(body, want_return))
                return lines
            kw = "if" if first else "elif"
            lines.append(f"{kw} {self.emit_expr(test, PREC_LOWEST)}:")
            lines += indent(self.emit_stmt(body, want_return))
            first = False
        if want_return:                 # 아무 절도 참이 아니면 머꼬는 공(nil) 반환
            lines.append("else:")
            lines += indent(["return []"])
        return lines

    def emit_let_stmt(self, args, want_return):
        lines = []
        for b in to_list(args[0]):
            var, val = b.car(), b.cdr().car()
            lines.append(f"{self.mangle(var.value())} = {self.emit_expr(val, PREC_LOWEST)}")
        lines += self.emit_stmt(args[1], want_return)
        return lines

    def emit_do_stmt(self, args, want_return):
        if not args:
            return ["return []"] if want_return else []
        lines = []
        for i, e in enumerate(args):
            lines += self.emit_stmt(e, want_return and i == len(args) - 1)
        return lines

    def emit_define(self, args, toplevel):
        target = args[0]
        if target.ispair():
            fname = self.mangle(target.car().value())
            params = self.param_names(target.cdr())
            body = args[1:]
            body_lines = []
            for i, e in enumerate(body):
                body_lines += self.emit_stmt(e, i == len(body) - 1)
            return [f"def {fname}({', '.join(params)}):"] + indent(body_lines)
        if target.issymbol():
            name = self.mangle(target.value())
            return [f"{name} = {self.emit_expr(args[1], PREC_LOWEST)}"]
        raise TransUnsupported("정의 대상이 올바르지 않습니다.", getattr(target, "line", None))

    def emit_toplevel(self, expr):
        if expr.ispair() and expr.car().issymbol():
            name = expr.car().value()
            if name == "정의":
                return self.emit_define(to_list(expr.cdr()), toplevel=True)
            if name == "매크로":
                raise TransUnsupported("매크로는 v1에서 지원하지 않습니다.",
                                       getattr(expr, "line", None))
        return self.emit_stmt(expr, want_return=False)

    def transpile(self, exprs):
        # Emit all top-level expressions and group them
        emitted = [self.emit_toplevel(e) for e in exprs]
        blocks = []
        i = 0
        while i < len(emitted):
            # Check if this block is multi-line (function definition)
            if len(emitted[i]) > 1:
                # Multi-line block: add as-is
                blocks.append("\n".join(emitted[i]))
                i += 1
            else:
                # Single-line block: group with consecutive single-line blocks
                group = []
                while i < len(emitted) and len(emitted[i]) == 1:
                    group.extend(emitted[i])
                    i += 1
                blocks.append("\n".join(group))

        header = (
            f"# 이 파일은 머꼬 소스 '{self.src_name}'에서 자동 번역된 Python 코드입니다.\n"
            "# 주의: '/'는 정수 나눗셈(//)으로, '읽기'는 int(input())으로 번역됩니다."
        )
        parts = [header]
        if self.needs_functools:
            parts.append("import functools")
        parts.extend(blocks)
        return "\n\n".join(parts) + "\n"


def transpile_file(exprs, src_name="<소스>"):
    return Transpiler(src_name).transpile(exprs)


def transpile_source(src, src_name="<소스>"):
    return transpile_file(parse_string(src), src_name)
