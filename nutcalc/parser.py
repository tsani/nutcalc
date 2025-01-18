from .syntax import *

from parsy import generate, string, regex, alt, seq, char_from, digit, fail

def file_module(f):
    """Parses an entire file. Returns a Module."""
    contents = f.read() # XXX find a way to avoid buffering the whole file
    return (junk >> module).parse(contents)

def line(line: str):
    """Parses one statement."""
    return (junk >> stmt).parse(line)

### LEXING ############################################################

space = char_from(' \t\n\r')
lexeme = lambda p: p << junk

line_comment = (string('#') << regex('[^\n]*') << space.many()).many()

junk = space.many() << line_comment.optional()

point = string('.')
digits = digit.at_least(1).concat()

number = lexeme(
    (digits + (point + digits).optional(default='.'))
    .map(lambda parts: ''.join(parts))
    .map(float)
).desc('number')

operator = lambda c: lexeme(string(c))

@generate
def string_literal():
    name = yield alt(string('\''), string('"'))
    body = yield regex(f'[^{name}]+')
    yield string(name)
    return body

ident = alt(
    regex('[a-zA-Z][0-9a-zA-Z]*').desc('bare name'),
    string_literal.desc('quoted name'),
)
ident = lexeme(ident)

add_op = operator("+").map(lambda _: lambda y: lambda x: x + y).desc('plus')
mul_op = operator("*").map(lambda _: lambda y: lambda x: x * y).desc('times')
div_op = operator("/").map(lambda _: lambda y: lambda x: x / y).desc('slash')

### ARITHMETIC ############################################################

@generate('arithmetic expression')
def arith():
    first = yield term
    fns = yield seq(add_op, term).map(lambda l: l[0](l[1])).many()
    for f in fns:
        first = f(first)
    return first

@generate('term')
def term():
    first = yield factor
    fns = yield seq(mul_op | div_op, factor).map(lambda l: l[0](l[1])).many()
    for f in fns:
        first = f(first)
    return first

factor = number | (operator("(") >> arith << operator(")")).desc(
    'parenthesized expression',
)

### FOOD EXPRESSIONS ##########################################################

quantity = seq(arith, ident).mark().combine(
    lambda start, x, end: Quantity(
        count=x[0],
        unit=x[1],
        location=SourceSpan(start, end),
    ),
)
quantified_food = seq(quantity, ident).mark().combine(
    lambda start, x, end: QuantifiedFood(
        quantity=x[0],
        food=x[1],
        location=SourceSpan(start, end),
    ),
)
expr = quantified_food.sep_by(operator('+'), min=1).mark().combine(
    lambda start, body, end: Expr(body, location=SourceSpan(start, end)),
)
bullet_expr = (operator('-') >> expr).at_least(1).map(
    lambda xss: [x for xs in xss for x in xs]
).mark().combine(
    lambda start, body, end: Expr(body, location=SourceSpan(start, end)),
)

### STATEMENTS ################################################################

@generate
def definition_stmt():
    lhs = yield quantified_food
    weight = yield (operator('weighs') >> quantity).optional()
    op = yield operator('=') | operator(':')

    if op == '=':
        rhs = yield expr | quantity

        match rhs:
            case Quantity():
                rhs = [QuantifiedFood(rhs, lhs.food)]

        if len(rhs) == 1 and rhs[0].food == lhs.food:
            if weight is not None:
                yield fail('unit definition forbids a `weighs` clause')
            return WeightStmt(lhs, rhs[0])
        else:
            return FoodStmt(lhs, weight, rhs)

    if op == ':':
        rhs = yield bullet_expr
        return FoodStmt(lhs, weight, rhs)

stmt_ = alt(
    (operator('print') >> expr).mark().combine(
        lambda start, e, end: PrintStmt(e, location=SourceSpan(start, end))
    ),
    definition_stmt,
)

def span_stmt(start, stmt, end):
    stmt.location = SourceSpan(start, end)
    return stmt
stmt = stmt_.mark().combine(span_stmt)

### MODULE ####################################################################

import_stmt = (operator('import') >> ident).mark().combine(
    lambda start, e, end: ImportStmt(e, location=SourceSpan(start, end)),
)

module = seq(import_stmt.many(), stmt.many()).combine(Module)
