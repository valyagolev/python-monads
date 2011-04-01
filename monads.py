import inspect
import collections

# BASIC API

def do(*actions):
    return reduce(lambda c, n: n.bind(c), reversed(actions))
    
def mreturn(l):
    return MReturn(l)


# MONADS THEMSELVES

class Monad(object):

    # Implement these please:
    
    @staticmethod
    def mreturn(v):
        """a -> M a"""
        raise NotImplementedError

    def bind(self, f):
        """
        M a -> (value -> context -> M b) -> M b

        please take a look on List and Maybe implementations"""
        raise NotImplementedError

    def run(self, context={}):
        """
        M a -> a

        please call self.apply(context) and then modify the result
        """
        raise NotImplementedError
    
    # Utils
    
    def __init__(self, it):
        self.it = it
    
    def __neg__(self):
        return PrepareBinding(self)

    def __call__(self, _, context):
        return self.apply(context)
    
    def apply(self, context):
        context['_monad'] = self.__class__
        return lambda_context_call(self.it, context)
    
    
class List(Monad):
    @staticmethod
    def mreturn(v):
        return [v]

    def bind(self, f):
        def bound(**ct):
            for i in self.apply(ct):
                for j in f(i, ct):
                    yield j
        
        return List( bound )

    
    def run(self, context={}):
        return list(self.apply(context))

class Maybe(Monad):
    @staticmethod
    def mreturn(v):
        return (True, v)

    def bind(self, f):
        def bound(**ct):
            t, v = self.apply(ct)
            if not t:
                return (False, False)
            else:
                return f(v, ct)
        
        return Maybe( bound )

    def run(self, context={}):
        return self.apply(context)


class Probability(Monad):
    @staticmethod
    def mreturn(v):
        return [(v, 1)]

    def bind(self, f):
        def bound(**ct):
            # can't do lazily (dont know how)

            nexts = []
            for val1, prob1 in self.apply(ct):
                for val2, prob2 in f(val1, ct):
                    nexts.append( (val2, prob1 * prob2) )
            
            print "nexts: ", nexts
            
            return nexts
            
        return Probability( bound )

    def run(self, context={}):
        d = collections.defaultdict(int)
        
        for v, p in self.apply(context):
            d[v] += p

        return d.items()

    
# MONADIC FUNCTIONS

def guard(l):

    def guard_it(**kwargs):
        if lambda_context_call(l, kwargs):
            yield None
        
        
                
    return HelperMonad(guard_it)




def tests():
    r = [ Var('a') <- List(lambda ct: [1, 2, 3]),
          Var('b') <- List(lambda ct: [1, 2, 3]),
          MReturn(List, lambda a, b: (a, b) )  ]

    print list(RunList(r).apply({}))

    r = [ Var('a') <- List(lambda ct: [1, 2, 3]),
          Var('b') <- List(lambda ct: [ct['a'] * 10, ct['a'] * 50]),
          #      MGuard(List, lambda ct: ct['b'] < 100),
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



# UTILS
    
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
    


class HelperMonad(Monad):
    def apply(self, context):
        return lambda_context_call(self.it, context)
    
    def bind(self, f):
        def bound(**ct):
            for j in self.apply(ct):
                for i in f(None, ct):
                    yield i

        return HelperMonad( bound )


class MReturn(HelperMonad):
    def __init__(self, l):
        self.l = l

    def apply(self, context):
        val = lambda_context_call(self.l, context)
        return context['_monad'].mreturn( val )

    
def lambda_context_call(l, context):
    sp = inspect.getargspec(l)
    
    if sp.keywords:
        return l(**context)
    else:
        args = dict((k, v) for k, v in context.iteritems()
                    if k in sp.args)
        return l(**args)
