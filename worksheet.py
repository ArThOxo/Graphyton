from modules.open_digraph import *


n0 = node(0, 'a', {3:1, 4:1}, {1:1, 2:1})
n1 = node(1, 'b', {0:1}, {2:2, 5:1})
n2 = node(2, 'c', {0:1, 1:2}, {6:1})
i0 = node(3, 'i0', {}, {0:1})
i1 = node(4, 'i1', {}, {0:1})
o0 = node(5, 'o0', {1:1}, {})
o1 = node(6, 'o1', {2:1}, {})


G = open_digraph([3,4], [5,6], [n0,n1,n2,i0,i1,o0,o1])
print(n0)
print(G)
