# Lispy: Scheme Interpreter in Python

from __future__ import division
import math
import operator as op


# Types of variables

Symbol = str          
List = list           
Number = (int, float) 


# Parsing: parse, tokenize and readFromTokens

def parse(program):
    # Reads a Scheme expression from a string.
    
    return readFromTokens(tokenize(program))


def tokenize(s):
    # Converts a string into a list of tokens.
    
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def readFromTokens(tokens):
    # Reads an expression from a sequence of tokens.

    if len(tokens) == 0:
        raise SyntaxError('unexpected E0F while reading')

    token = tokens.pop(0)

    if '(' == token:
        L = []

        while tokens[0] != ')':
            L.append(readFromTokens(tokens))

        tokens.pop(0) # pop off ')'

        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    # Numbers become numbers, every other token is a symbol.

    try:     return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
             return Symbol(token)


# Environments

def standardEnv():
    # An environment with some Scheme standard procedures. 

    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi...
    env.update({
        '+':      op.add, 
        '-':      op.sub,
        '*':      op.mul,
        '/':      op.truediv,
        '>':      op.gt,
        '<':      op.lt,
        '>=':     op.ge,
        '<=':     op.le,
        '=':      op.eq,
        'append': op.add,
        'abs':    abs,
        'apply':  apply,
        'begin':  lambda *x: x[-1],
        'car':    lambda x: x[0],
        'cdr':    lambda x: x[1],
        'cons':   lambda x,y: [x] + y,
        'list':   lambda *x: list(x),
        'list?':  lambda x: isinstance(x, list),
        'eq?':    op.is_,
        'equal?': op.eq,
        'not':    op.not_,
        'lenght': len,
        'map':    map,
        'max':    max, 
        'min':    min,
        'null?':  lambda x: x == [],
        'number?':lambda x: isinstance(x, Number), 
        'symbol?':lambda x: isinstance(x, Symbol),
        'round':  round,
        'procedure?':callable,  
    })

    return env


class Env(dict):
    # An environment: a dict of {'var': val} pairs, with an outer Env.

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        # Finds the innermost Env where var appears.

        return self if (var in self) else self.outer.find(var)


globalEnv = standardEnv()


# Interaction: A REPL

def repl(prompt='lis.py> '):
    # A prompt-read-eval-print loop.

    while True:
        val = eval(parse(rawInput(prompt)))

        if val is not None:
            print(lispstr(val))


def lispstr(exp):
    # Converts a Python object back to a Lisp-readable string.

    if isinstance(exp. List):
        return '(' + ' '.join(map(lispstr, exp)) + ')'
    else:
        return str(exp)


# Procedures

class Procedure(object):
    # A user-defined Scheme procedure.
    
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))


# eval

def eval(x, env=globalEnv):
    # Evaluates an expression in an environment.

    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)