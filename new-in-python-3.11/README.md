# New in Python 3.11

I've gone through the new features of 3.11 and selected my personal highlights.
Most of this is based on the [release notes
highlights](https://www.python.org/downloads/release/python-3110/), but I've
also added a few bits and pieces of my own from the [detailed release
notes](https://docs.python.org/3/whatsnew/3.11.html).

## General interpreter improvements

There are two major improvements to the interpreter: speed and detailed
tracebacks.

### [SPEEEEED!](https://docs.python.org/3/whatsnew/3.11.html#faster-cpython)

CPython is now [10-60% faster (25% on
average)](https://docs.python.org/3/whatsnew/3.11.html#faster-cpython)

* [Frozen imports of core Python modules](https://docs.python.org/3/whatsnew/3.11.html#frozen-imports-static-code-objects): Core python modules are now statically allocated by the interpreter, significantly speeding up startup times compared to when cached bytecode needed to be read, unmarshalled and put on the heap before evaluation.
* [Inlined pure-Python function calls](https://docs.python.org/3/whatsnew/3.11.html#inlined-python-function-calls): When CPython detects a Python function calling another Python function, it can simply "jump" to the called function, bypassing the C function otherwise evaluated on the code. Is this implemented with a `goto`, you might ask? [Of course it is](https://github.com/pablogsal/cpython/blob/v3.11.0/Python/ceval.c#L4762).
* [Specializing Adaptive Interpreter](https://docs.python.org/3/whatsnew/3.11.html#pep-659-specializing-adaptive-interpreter): This one is _cool_. CPython will attempt to optimize hot code paths on the fly (along the lines of a JIT), for example by using faster code paths for certain operations (e.g. binary operations on integers), caching attribute indices to avoid namespace (dictionary) lookups, and much more!
    - Podcast on the topic: [TalkPython Episode 318 - Python Perf: Specializing, Adaptive Interpreter](https://talkpython.fm/episodes/show/381/python-perf-specializing-adaptive-interpreter)

### [Detailed tracebacks](https://docs.python.org/3/whatsnew/3.11.html#pep-657-fine-grained-error-locations-in-tracebacks)

Tracebacks now contain [detailed positional
information](https://docs.python.org/3/whatsnew/3.11.html#pep-657-fine-grained-error-locations-in-tracebacks).
That's _really_ nice for beginners, but also when you've been thrown into a
legacy code base where you've no idea where that `'NoneType' Object has no
attribute ...`
error is comming from. Here's

```python
first = []
second = None

if len(first) >= 0 and len(first) > len(second):
    print("Yep")
```

Prior to 3.11 you would get this traceback, which does not indicate what part of
the expression failed:

```bash
Traceback (most recent call last):
  File "/home/slarse/Documents/github/work/hiq/talks/new-in-python-3.11/exc.py", line 4, in <module>
    if len(first) >= 0 and len(first) > len(second):
TypeError: object of type 'NoneType' has no len()
```

In 3.11, you get a clear indication of what part failed:

```bash
Traceback (most recent call last):
  File "/home/slarse/Documents/github/work/hiq/talks/new-in-python-3.11/exc.py", line 4, in <module>
    if len(first) >= 0 and len(first) > len(second):
                                        ^^^^^^^^^^^
TypeError: object of type 'NoneType' has no len()
```

## Exceptions

There are two notable additions to exceptions: exception groups and notes.

### [Exception notes](https://docs.python.org/3/whatsnew/3.11.html#whatsnew311-pep678)

You can now add notes to exceptions to enhance them. This is useful to add
information as an exception propagates up a series of try/excepts.

```python
try:
    raise ValueError("I don't know much down here")
except ValueError as e:
    e.add_note("But here where I'm catching it I know something more")
    raise
```

The note is simply appended to the error message.

```
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
ValueError: I don't know much down here
But here where I'm catching it I know something more
```

### [Exception groups](https://peps.python.org/pep-0654/)

Exception groups allow you to propagate multiple potentially unrelated
exceptions as one unit. What's really cool is that arbitrary exceptions can
be propagated together, as a group, but handled by type using the new `except*`
syntax.

The primary use case for exception groups is for asynchronous/parallel
execution, where multiple threads, processes or couroutines may raise different
exceptions that all need to be propagated and handled.

```python
def function_that_raises():
    raise ExceptionGroup(
        "Unexpected problem :(",
        [RuntimeError("!"), TypeError("Oh"), ValueError("No")],
    )

def main():
    try:
        function_that_raises()
    except* TypeError as subgroup:
        for e in subgroup.exceptions:
            print(f"Handled the type error with {e}")
    except* ValueError as subgroup:
        for e in subgroup.exceptions:
            print(f"Handled the value error with {e}")
    except* Exception as subgroup:
        for e in subgroup.exceptions:
            print(f"Handled other exception with {e}")

if __name__ == "__main__":
    main()
```

We found during the talk that it's also fine to catch a non-grouped exception
with `except*`.

```python
try:
    raise TypeError("Not grouped!")
except* TypeError as subgroup:
    for e in subgroup.exceptions:
        print(f"Handled the type error with {e}")
```

## Asyncio

Asyncio has gotten quite a lot of love in 3.11. Task groups are (for some
reason) the big standout according to the [release
notes](https://docs.python.org/3/whatsnew/3.11.html), but there's a lot more to
find if you dig a little deeper.

### [Task groups](https://docs.python.org/3/library/asyncio-task.html#task-groups)

Task groups provide a high level interface for creating tasks through the the
`asyncio.TaskGroup` class, which is designed to be used as a context manager.
Task groups make it effortless to start a bunch of coroutines and wait for them
all to finish.

```python
import asyncio

async def main_with_task_groups():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(slow_coroutine())
        tg.create_task(fast_coroutine())

    print(f"All done!")

async def slow_coroutine():
    print("Slow start")
    await asyncio.sleep(3)
    print("Slow end")

async def fast_coroutine():
    print("Fast start")
    await asyncio.sleep(1)
    print("Fast end")

if __name__ == "__main__":
    asyncio.run(main_with_task_groups())
```

The corresponding code before 3.11 would need to use `asyncio.gather`.

```python
async def main_without_task_groups():
    slow_task = asyncio.create_task(slow_coroutine())
    fast_task = asyncio.create_task(fast_coroutine())

    await asyncio.gather(slow_task, fast_task)
    print("All done!")
```

### [Runner context manager](https://docs.python.org/3/library/asyncio-runner.html#runner-context-manager)

While most `asyncio` programs should be executed through `asyncio.run()`, there
are cases where that doesn't quite fit the bill. `asyncio.run()` always creates
a new loop, runs the task and then closes the loop. If you want to run multiple
top-level tasks that's inefficient, but this is remedied by the new `Runner`
context manager which keeps an internal event loop running.

The `Runner` also allows for overlapping event loops, whereas `asyncio.run()`
will fail if there is already an event loop running.

```python
import asyncio

def main():
    with asyncio.Runner() as runner:
        runner.run(hello("World"))

        with asyncio.Runner() as nested_runner:
            # no problem creating a new event loop while the first one is still running
            nested_runner.run(hello("Nested"))

        runner.run(hello("There"))

async def hello(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

### [Timeouts](https://docs.python.org/3/library/asyncio-task.html#timeouts)

A simple but sorely needed feature: timeouts for asyncio tasks!

```python
import asyncio

async def main():
    async with asyncio.timeout(delay=2):
        await incredibly_slow_coroutine()

async def incredibly_slow_coroutine():
    print("Start slow coroutine")
    await asyncio.sleep(10)
    print("End slow coroutine")

if __name__ == "__main__":
    asyncio.run(main())
```

We can also combine this with any of the aforementioned context managers (such
as a task group) and get the expected result.

```python
async def main_with_task_group():
    async with asyncio.timeout(delay=2), asyncio.TaskGroup() as tg:
        tg.create_task(incredibly_slow_coroutine())
```

## Typing
There are a bunch of new type hint features, but there was really only one that
I think is relevant to most users that aren't library maintainers (and library
maintainers don't need this summary anyway).

### `Self` type
Classes can now finally refer to themselves!

Initially when type hints were introduced in Python 3.5, we had to "self type"
like so:

```python
class SincePython3_5:
    def __init__(self) -> "SincePython3_5":
        pass
```

With Python 3.7, we could discard the quotes by importing the `annotations`
future flag.

> Note: This functionality is currently [not a sure
> thing](https://docs.python.org/3/whatsnew/3.11.html#pep-563-may-not-be-the-future)
> and may be removed.

```python
from __future__ import annotations


class SincePython3_7:
    def __init__(self) -> SincePython3_7:
        pass
```

Now in Python 3.11, we can finally do it the sane way!

```python
class SincePython3_11:
    def __init__(self) -> Self:
        pass
```
