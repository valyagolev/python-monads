        
class Monad(object):
    def __neg__(self):
        return PrepareBinding(self)

    def __init__(self, it):
        self.it = it
    
    def apply(self, context):
        return self.it(context)
    
class List(Monad):
    @staticmethod
    def mreturn(v):
        return [v]

    def bind(self, f):
        def bound(ct):
            for i in self.apply(ct):
                for j in f(i, ct):
                    yield j
        
        return List( bound )

class Maybe(Monad):
    @staticmethod
    def mreturn(v):
        return (True, v)

    def bind(self, f):
        def bound(ct):
            t, v = self.apply(ct)

            if not t:
                return (False, False)

            return f(v, ct)
        
        return Maybe( bound )
        

"""

do i <- [1,2,3]
   j <- [1,2,3]
   return j

function r1(context):

context['j'] = r1
   return context
   
function r2(context):
   return context['j']

"""

# UTILS FOR BINDING


class Var(object):
    def __init__(self, name):
        self.name = name

    def __lt__(self, mb):
        return BindName(self.name, mb.m)

class PrepareBinding(object):
    def __init__(self, m):
        self.m = m

class BindName(object):
    def __init__(self, name, fr):
        self.name = name
        self.fr = fr

    def bind(self, to):

        def f(v, context):
            """ value -> monad """
            new_context = dict(context)
            new_context[self.name] = v

            return to.apply(new_context)
        
        return self.fr.bind(f)

# RETURN
    
class MReturn(object):
    def __init__(self, m, l):
        self.l = l
        self.m = m

    def apply(self, context):
        return self.m.mreturn( self.l(**context) )


    
# UTILS

def RunList(l):
    t = l[-1]
    
    for i in reversed(l[:-1]):
        t = i.bind(t)

    return t


r = [ Var('a') <- List(lambda ct: [1, 2, 3]),
      Var('b') <- List(lambda ct: [1, 2, 3]),
      MReturn(List, lambda a, b: (a, b) )  ]

print list(RunList(r).apply({}))

r = [ Var('a') <- List(lambda ct: [1, 2, 3]),
      Var('b') <- List(lambda ct: [ct['a'] * 10, ct['a'] * 50]),
      MGuard(List, lambda ct: ct['b'] < 100),
      MReturn(List, lambda a, b: (a, b) )  ]

print list(RunList(r).apply({}))


r = [ Var('a') <- Maybe(lambda ct: (True, 7)),
      Var('b') <- Maybe(lambda ct: (True, 123)),
      MReturn(Maybe, lambda a, b: (b, a) )  ]

print RunList(r).apply({})

r = [ Var('a') <- Maybe(lambda ct: (True, 7)),
      Var('b') <- Maybe(lambda ct: (False, False)),
      Var('c') <- Maybe(lambda ct: 123 / 0),
      MReturn(Maybe, lambda a, c: (c, a) )  ]


print RunList(r).apply({})
