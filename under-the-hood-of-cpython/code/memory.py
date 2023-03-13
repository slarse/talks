import tracemalloc
tracemalloc.start()

numbers = list(range(1_000_000))

print("Current: %d, Peak %d" % tracemalloc.get_traced_memory())
