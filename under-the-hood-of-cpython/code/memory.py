import tracemalloc
tracemalloc.start()

numbers = list(range(1_000_000))

print(tracemalloc.get_traced_memory())
