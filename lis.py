# Lispy: Scheme Interpreter in Python

from __future__ import division
import math
import operator as op
import functools


# Types of variables

Symbol = str
List = list
Number = (int, float)


# Parsing: parse, tokenize and read_from_tokens

def parse(program):
    "Reads a Scheme expression from a string."

    return read_from_tokens(tokenize(program))


def tokenize(string_input):
    "Converts a string into a list of tokens."

    return string_input.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens):
    " Reads an expression from a sequence of tokens."

    if not tokens:
        raise SyntaxError('unexpected E0F while reading')

    token = tokens.pop(0)

    if token == '(':
        L = []

        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))

        tokens.pop(0) # pop off ')'

        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    " Numbers become numbers, every other token is a symbol."

    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


# Environments

def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   functools.partial,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env


class Env(dict):
    " An environment: a dict of {'var': val} pairs, with an outer Env. "

    def __init__(self, parms=(), args=(), outer=None):
        super().__init__()
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Evaluate an expression in an environment."
        return self if (var in self) else self.outer.find(var)


GLOBAL_ENV = standard_env()


# Interaction: A REPL

def repl(prompt='lis.py> '):
    " A prompt-read-evaluate    -print loop. "

    while True:
        val = evaluate(parse(input(prompt)))

        if val is not None:
            print(lispstr(val))


def lispstr(exp):
    " Converts a Python object back to a Lisp-readable string."

    if isinstance(exp. List):
        return '(' + ' '.join(map(lispstr, exp)) + ')'
    else:
        return str(exp)


# Procedures

class Procedure(object):
    " A user-defined Scheme procedure. "

    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return evaluate(self.body, Env(self.params, args, self.env))


def evaluate(x, env=GLOBAL_ENV):
    " Evaluates an expression in an environment."
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        exp = (conseq if evaluate(test, env) else alt)
        return evaluate(exp, env)
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'lambda':
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = evaluate(x[0], env)
        args = [evaluate(exp, env) for exp in x[1:]]
        return proc(*args)