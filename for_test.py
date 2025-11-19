import main
import inspect
import sys

from main import app

print("APP =", app)

# где определён модуль main?
print("MAIN MODULE =", main)
print("MAIN MODULE FILE =", inspect.getfile(main))

# где лежит сам файл?
print("SYS MODULE PATH =", sys.modules['main'].__file__)
