import traceback
try:
    x = 10/0
except Exception as e :
    print(traceback.format_exc())

l = [92,34,32,423,423,42,342,34,2,12421,4]
print(l)
del l[6:]
print(l)