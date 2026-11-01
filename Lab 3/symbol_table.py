# Python wrapper around the C symbol table (symbol_table.c).
# The hash table itself is written in C; this file only loads the compiled
# library with ctypes and calls its functions. If the library is not compiled
# yet, it compiles it with gcc.

import ctypes
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C_FILE = os.path.join(HERE, "symbol_table.c")
if sys.platform == "win32":
    LIB_FILE = os.path.join(HERE, "st_lib.dll")
    COMPILE = ["gcc", "-shared", "-o", LIB_FILE, C_FILE]
else:
    LIB_FILE = os.path.join(HERE, "st_lib.so")
    COMPILE = ["gcc", "-shared", "-fPIC", "-o", LIB_FILE, C_FILE]

if not os.path.exists(LIB_FILE) or os.path.getmtime(LIB_FILE) < os.path.getmtime(C_FILE):
    subprocess.run(COMPILE, check=True)

lib = ctypes.CDLL(LIB_FILE)
INT_P = ctypes.POINTER(ctypes.c_int)

lib.st_create.argtypes = [ctypes.c_int]
lib.st_create.restype = ctypes.c_void_p
lib.st_hash.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.st_hash.restype = ctypes.c_int
lib.st_search.argtypes = [ctypes.c_void_p, ctypes.c_char_p, INT_P, INT_P]
lib.st_search.restype = ctypes.c_int
lib.st_add.argtypes = [ctypes.c_void_p, ctypes.c_char_p, INT_P, INT_P]
lib.st_add.restype = None
lib.st_get.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.st_get.restype = ctypes.c_char_p
lib.st_count.argtypes = [ctypes.c_void_p]
lib.st_count.restype = ctypes.c_int
lib.st_write.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.st_write.restype = ctypes.c_int
lib.st_destroy.argtypes = [ctypes.c_void_p]
lib.st_destroy.restype = None


class SymbolTable:
    def __init__(self, size=31):
        self.table = lib.st_create(size)

    def hash(self, key):
        return lib.st_hash(self.table, key.encode())

    def search(self, key):
        b = ctypes.c_int()
        i = ctypes.c_int()
        if lib.st_search(self.table, key.encode(), ctypes.byref(b), ctypes.byref(i)):
            return (b.value, i.value)
        return None

    def add(self, key):
        b = ctypes.c_int()
        i = ctypes.c_int()
        lib.st_add(self.table, key.encode(), ctypes.byref(b), ctypes.byref(i))
        return (b.value, i.value)

    def get(self, pos):
        value = lib.st_get(self.table, pos[0], pos[1])
        return None if value is None else value.decode()

    def count(self):
        return lib.st_count(self.table)

    def write(self, file_name):
        lib.st_write(self.table, file_name.encode())

    def __del__(self):
        if self.table:
            lib.st_destroy(self.table)
            self.table = None
