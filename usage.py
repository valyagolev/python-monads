
from monads import do, List, Maybe, Probability, mreturn, Var, guard

l1 = do( Var('a') <- List(lambda: [1, 2, 3]),
         mreturn(lambda a: a + 1) )

print l1.run()

l2 = do( Var('a') <- List(lambda: [1, 2, 3]),
         Var('b') <- List(lambda a: [a + 1, a + 9, a * 40]),
         Var('c') <- List(lambda a: xrange(a + 5)),
         guard(lambda b: b < 30),
         mreturn(lambda b, c: (b, c)) )

print l2.run()

l3 = do( Var('a') <- List(lambda: [1,2,3]),
         Var('b') <- List(lambda a: [a * 10, a * 20]),
         guard(lambda b: b <= 20),
         mreturn(lambda a, b: (a, b)) )

print l3.run()

l4 = do( Var('a') <- Maybe(lambda: (True, 7)),
         Var('b') <- Maybe(lambda: (True, 123)),
         mreturn(lambda a, b: (b, a) )  )

print l4.run()


l5 = do( Var('a') <- Maybe(lambda: (True, 7)),
         Var('b') <- Maybe(lambda: (False, False)),
         Var('c') <- Maybe(lambda a: a / 0),
         mreturn(lambda a, c: (c, a) ) )

print l5.run()


# probability of each side of a coin:

coin = Probability(lambda: [(1, 0.5), (0, 0.5)])

l6 = do( Var('c') <- coin,
         mreturn(lambda c: c) )

print l6.run()

l7 = do( Var('first_coin') <- coin,
         Var('second_coin') <- coin,
         mreturn(lambda first_coin, second_coin:
                     (first_coin, second_coin)) )

print l7.run()

# probability of coins being equal

l8 = do( Var('fc') <- coin,
         Var('sc') <- coin,
         mreturn(lambda fc, sc: fc == sc) )

print l8.run()
