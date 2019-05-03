
#
# Written by Antti Karttunen (Email: his-firstname.his-surname@gmail.com)
# around 2008 and the new decorators CachedMatchesFrom0, etc in July 20 2014
#
# (Just as a proof of concept that it works also in Python)
#
# Public Domain - Please feel free to use and improve these ideas for 
# (hopefully equally Open Source) Python/Sage libraries, etc.
# At least: find an appropriate integer type that can store arbitrarily
#  large integers without losing any precision!
#
# After that is done, one could port also other functionals from
#   https://github.com/karttu/IntSeq/blob/master/src/transforms.scm
# to Python, e.g. RECORD-POS, DISTINCT-POS (use a hash table instead of vector)
# etc.
#
# See also:
#   http://www.luschny.de/blog/The_Unofficial_Guide_to_Coding_for_the_OEIS.html
#

#
# matching1pos renamed to CachedMatchesFrom0
#

# Say: from memotest import *


from array import *

def gen_n_items(n,item):
  for i in xrange(n): yield(item)

# About the same as CachedFunction in Sage:
def memoed(fun):
    maxmemosize = 131 # 072
    notfilled = 0L
    memo = array('L')
    def wrapper(n):
        memsiznow = len(memo)
        if None == n: return(memo) # For debugging
        elif n >= memsiznow:
              newsize = min(maxmemosize,max(n+1,2*memsiznow))
              memo.extend(gen_n_items(newsize-memsiznow,notfilled))

        res = memo[n]
        if(notfilled == res):
              res = fun(n)
              memo[n] = res
              return(res)
        else: return(res)
    return wrapper



# The original, partly recursive implementation:
# This corresponds approximately to (MATCHING-POS 1 0 fun) in that IntSeq-library.

def CachedMatchesFrom0_recursive_implementation(fun):
    notfilled = 0L
    memo = array('L')
    def wrapper(n):
        memsiznow = len(memo)
        if None == n: return(memo) # For debugging
        elif n >= memsiznow:
            newsize = max(n+1,2*memsiznow)
            memo.extend(gen_n_items(newsize-memsiznow,notfilled))

        res = memo[n]
        if(notfilled == res): # Not yet in memo?
            if 1 == n: # If the caller asks the first number satisfying the condition, start searching from n=1.
              i = 0
            else: # Otherwise, start searching from one past where the prev term satisfying the condition was found
# Note: with this stack might overflow if computing terms in non-monotone order and "peeking too much ahead":
              i = 1 + wrapper(n-1)
# Then start searching the next positive integer matching the condition:
            while True:
              if fun(i):
                memo[n] = i
                return(i)
              else: # Keep on searching...
                i = i+1

        else: return(res) # We had that term already memoized, just return it.
    return wrapper


# This version works even when computing first say term a(10000) as it will
# search and memoize all the values a(0) .. a(9999) internally, in a loop.
# This corresponds approximately to (MATCHING-POS 1 0 fun) in my IntSeq-library.
# Start searching from the integers k which result fun(k) = True from k=0 onward,
# the first that is found will be the value of a(1) of the defined function.

def CachedMatchesFrom0(fun):
    notfilled = 0L
    memo = array('L',[0])
    def wrapper(n):
        memsiznow = len(memo)
        if None == n: return(memo) # For debugging
        elif n >= memsiznow:
# We have to allocate more space for memo-vector. Assuming here that such
# regrowths are expensive, so we are doing it in chunks of ever-doubling size.
# (I'm not sure whether this is actually true with Python-arrays. And in any
# case, gen_n_items iterator is called for each element to be added):
            newsize = max(n+1,2*memsiznow)
            memo.extend(gen_n_items(newsize-memsiznow,notfilled))

        um = memo[0]

        if(n <= um): return(memo[n]) # Has been computed before, take the value from memo.
        else: # Not yet in memo?
          if 0 == um: i = -1 # And memo is still empty? Then we start searching from i=0.
          else: i = memo[um] # Otherwise from one past the latest integer which matched the condition.

# Then search for the next positive integers matching the condition:
          while um < n: # Until we have finally found all the matching terms up to the n-th one.
            i = i+1
            if fun(i):                                # If the integer i matches the condition,
              um = um + 1                             # update the index of the highest computed term in memo
              memo[um] = i                            # and store i into theat position in the memo-vector

          memo[0] = um # Update the "effective size" of memo. (Here um = n).
          return(i)    # Return the found i to the caller.

    return wrapper


# This version corresponds approximately to (MATCHING-POS 1 1 fun) in IntSeq-library:
# Start searching from the integers k which result fun(k) = True from k=1 onward,
# the first that is found will be the value of a(1) of the defined function.

def CachedMatchesFrom1(fun):
    notfilled = 0L
    memo = array('L',[0])
    def wrapper(n):
        memsiznow = len(memo)
        if None == n: return(memo) # For debugging
        elif n >= memsiznow:
# We have to allocate more space for memo-vector. Assuming here that such
# regrowths are expensive, so we are doing it in chunks of ever-doubling size.
# (I'm not sure whether this is actually true with Python-arrays. And in any
# case, gen_n_items iterator is called for each element to be added):
            newsize = max(n+1,2*memsiznow)
            memo.extend(gen_n_items(newsize-memsiznow,notfilled))

        um = memo[0]

        if(n <= um): return(memo[n]) # Has been computed before, take the value from memo.
        else: # Not yet in memo?
# Get the latest positive integer which matched the condition (and was memoized)
          i = memo[um] # Note that if um = 0 then memo[0] = 0 and i will be 0 as well.

# Then search for the next positive integers matching the condition:
          while um < n: # Until we have finally found all the matching terms up to the n-th one.
            i = i+1
            if fun(i):                                # If the integer i matches the condition,
              um = um + 1                             # update the index of the highest computed term in memo
              memo[um] = i                            # and store i into theat position in the memo-vector

          memo[0] = um # Update the "effective size" of memo. (Here um = n).
          return(i)    # Return the found i to the caller.

    return wrapper


########################################################################

### Usage examples ###
# Try fibo(47) for example. (The last that fits into long!)

@memoed
def fibo(n):
  '''Fibonakin luvut, A000045.'''
  if(n < 2): return(n)
  else: return(fibo(n-2)+fibo(n-1))



@memoed
def A001477(n):
  '''Computes non-negative integers in funny way.'''
  if(n < 2): return(n)
  else: return(A001477(n-1)+(A001477(n-1)-A001477(n-2)))


# A224694: Numbers n such that n^2 AND n = 0, where AND is the bitwise logical AND operator.

def is_A224694(n):
  '''Does n satisfy: n^2 AND n = 0 ?'''
  return(0 == ((n*n) & n))

@CachedMatchesFrom0
def A224694(n):
  '''Numbers n such that n^2 AND n = 0, where AND is the bitwise logical AND operator.'''
  return(is_A224694(n))

# This is for testing the limits of recursion:
@CachedMatchesFrom0_recursive_implementation
def A224694_with_recursive_implementation(n):
  '''Numbers n such that n^2 AND n = 0, where AND is the bitwise logical AND operator.'''
  return(is_A224694(n))



# A213382: Numbers n such that n^n mod (n + 2) = n.

def is_A213382(n):
  '''Does n satisfy: n^n mod (n + 2) = n ?'''
# print "Calling is_A213382 with n=",n
  return(n == (n**n % (n+2)))

@CachedMatchesFrom1
def A213382(n): return(is_A213382(n))

@CachedMatchesFrom0_recursive_implementation
def A213382_with_recursive_implementation(n):
  '''Numbers n such that n^n mod (n + 2) = n.'''
  return(is_A213382(n))

# [A213382_with_recursive_implementation(10-n) for n in range(10)]
# Calling is_A213382 with n= 1
# Calling is_A213382 with n= 2
# Calling is_A213382 with n= 3
# ...
# Calling is_A213382 with n= 53
# Calling is_A213382 with n= 54
# Calling is_A213382 with n= 55
# [55, 49L, 37L, 31L, 19L, 16L, 13L, 7L, 4L, 1L]
# 


# >>> A213382(None)
# array('L', [0L])
# >>> A213382(1)
# Calling is_A213382 with n= 1
# 1L
# >>> A213382(5)
# Calling is_A213382 with n= 2
# Calling is_A213382 with n= 3
# ...
# Calling is_A213382 with n= 14
# Calling is_A213382 with n= 15
# Calling is_A213382 with n= 16
# 16L
# >>> A213382(None)
# array('L', [5L, 1L, 4L, 7L, 13L, 16L])
# >>> [A213382(10-n) for n in range(10)]
# Calling is_A213382 with n= 17
# Calling is_A213382 with n= 18
# Calling is_A213382 with n= 19
# Calling is_A213382 with n= 20
# Calling is_A213382 with n= 21
# ...
# Calling is_A213382 with n= 52
# Calling is_A213382 with n= 53
# Calling is_A213382 with n= 54
# Calling is_A213382 with n= 55
# [55L, 49L, 37L, 31L, 19L, 16L, 13L, 7L, 4L, 1L]
# >>> [A213382(10-n) for n in range(10)]
# [55L, 49L, 37L, 31L, 19L, 16L, 13L, 7L, 4L, 1L]
# >>> 
# 

# [A224694(n+1) for n in range(20)]
# [0L, 2L, 4L, 8L, 10L, 12L, 16L, 18L, 24L, 26L, 32L, 34L, 36L, 40L, 44L, 48L, 50L, 56L, 64L, 66L]

# A224694_with_recursive_implementation(None)
# array('L')
# >>> [A224694_with_recursive_implementation(10-n) for n in range(10)]
# [26, 24L, 18L, 16L, 12L, 10L, 8L, 4L, 2L, 0]
# >>> A224694_with_recursive_implementation(None)
# array('L', [0L, 0L, 2L, 4L, 8L, 10L, 12L, 16L, 18L, 24L, 26L])

# [A224694_with_recursive_implementation(n+1) for n in range(20)]
# [0, 2, 4L, 8L, 10L, 12L, 16L, 18L, 24L, 26L, 32L, 34L, 36L, 40L, 44L, 48L, 50L, 56L, 64L, 66L]


# Note:
# >>> A224694(10000)
# returns quickly 691968L
# (Cf. https://oeis.org/A224694/b224694.txt )
# but
# >>> A224694_with_recursive_implementation(10000)
# results:
# RuntimeError: maximum recursion depth exceeded in cmp
#   after a longish dump of lines like:
# File "memotest.py", line 69, in wrapper
#    i = 1 + wrapper(n-1)
#

