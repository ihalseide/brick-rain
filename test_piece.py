#!/usr/bin/env python3

#brick test
from bricks import Piece

p = Piece(shape='L')
print(p)
arr = p.get_array()
print(arr)
string_ = p.get_string(arr)
print(string_)