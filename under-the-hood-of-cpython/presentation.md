# Introduction

## Please forgive me, here's a logo

\begin{figure}
    \centering
    \includegraphics[width=.6\linewidth]{images/hiq_logo_black.png}
\end{figure}

## Who am I?

::: columns

:::: column

* Simon Larsén
* Software engineer at HiQ
* Open sourcerer
* Programming language enthusiast

::::

:::: column

### Contact and social media

* Email: slarse@slar.se
* GitHub: [https://github.com/slarse](https://github.com/slarse)
    - [https://github.com/slarse/talks](https://github.com/slarse/talks)
* [LinkedIn (LINK)](https://www.linkedin.com/in/simon-lars%C3%A9n-b665b3102/)

::::

:::

## Question for the audience


\begin{minipage}{\linewidth}
\centering \huge Is Python an interpreted or a compiled language?
\end{minipage}

## Both and neither!

### Python is a language specification

A language specification says what you are allowed to write
(syntax) and what should happen if you run something syntactically correct
(semantics).

### CPython is the reference implementation of the Python language

So called because it is written in C!

But there are other implementations, such as PyPy and Jython
[@python_alternate_implementations].

# CPython is compiled

## Compiled? Really?

### Running a program
When I run `python hello_world.py`, doesn't it just "interpret the text"?

No, that would be horrendously inefficient!

### CPython compiles to bytecode before execution

And executes said bytecode in the interpreter (which we are getting to)

\tikzset{
    module/.style={ellipse, draw=black, align=center, minimum width=15, thick},
    file/.style={rectangle, draw=black, align=center, thick}
}

\begin{tikzpicture}
    \node[file] (input) {hello\_world.py};
    \node[module, right=1cm of input] (compiler) {Compiler};
    \node[file, below=0.5cm of compiler] (bytecode) {hello\_world.pyc};
    \node[module, right=1cm of bytecode] (interpreter) {Interpreter};
    \node[file, below=0.5cm of interpreter] (output) {"Hello, world!"};

    \path [thick, black, ->]
    (input.east) edge (compiler.west)
    (compiler.south) edge (bytecode.north)
    (bytecode.east) edge (interpreter.west)
    (interpreter.south) edge (output.north);
\end{tikzpicture}

## Python bytecode

* Each instruction consists of an `opcode` and an `oparg`
    - Generally instructions are two bytes (one for `opcode`, one for `oparg`)
* We can view bytecode with the `dis` module [@dis_module]
    - `python -m dis <python_source_file>`
    - Bytecode is an implementation detail of CPython and changes often
    - But the principle has remained the same since the dawn of CPython

::: columns

:::: column

This Python code

```python
def hello_world():
    greeting = "Hello, world!"
    print(greeting)
```

::::

:::: column
Compiles to this bytecode

\scriptsize
\lstinputlisting{code/hello_world.bytecode}

::::

:::

# CPython is interpreted

## Bytecode evaluation

::: columns

:::: column

### The interpreter loop 

* Defined in `Python/ceval.c` [@python_source]
* "Endless" for loop
* Runs until the main module returns

### The interpreter is a stack machine!

* Computed values are pushed to the value stack
* Function arguments, return values etc are retrieved from the value stack

::::

:::: column

### Part of the interpreter loop

\tiny

```c
main_loop:
    for (;;) {
        // [...]
        switch (opcode) {
        // [...]
        case TARGET(LOAD_CONST): {
            PREDICTED(LOAD_CONST);
            PyObject *value = GETITEM(consts, oparg);
            Py_INCREF(value);
            PUSH(value);
            FAST_DISPATCH();
        }
        // [...]
        case TARGET(POP_TOP): {
            PyObject *value = POP();
            Py_DECREF(value);
            FAST_DISPATCH();
        }
        // [...]
        }
    }
```

::::

:::

## Frame objects

Python code is executed within a context called a _frame object_. When a
function is called, a new frame object is created and entered. When it returns,
the previous frame is entered and the returning function's frame is destroyed
(typically).

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    point/.style={circle, fill=black, thin, minimum width=.05cm}
}

\centering
\begin{tikzpicture}
    \node[square, label={Frame object (well, a partial one) for call to hello\_world()}, minimum width=300, minimum height=125] (stackbottom1) {};

    \node[square, label={Locals}, xshift=-4cm, yshift=1cm] (locals) {\texttt{greeting}\\...};

    \node[square, label={Globals}, right=1cm of locals] (globals) {\texttt{print}\\...};

    \node[square, below=.2cm of locals] (back) {f\_back};

    \node[square, below=.2cm of back] (lasti) {f\_lasti};

    \node[square, below=.2cm of lasti] (valuestack) {f\_valuestack};
    
    \node[square, label={Code}, right=.5cm of globals, yshift=-1cm] (bytecode) {
        \tiny \lstinputlisting{code/hello_world.bytecode}
    };

    \path [thick, black, dashed, ->]
    (lasti.east) edge (bytecode.west)
    ;

\end{tikzpicture}

## What is a stack?

A last-in-first-out (LIFO) data structure. We need to know about four
operations:

* Push: Put something on top of the stack.
* Pop: Remove and return the topmost value from the stack.
* Peek/top: Look at the topmost value on the stack without removing it.
* Set: Overwrite the top of the stack.

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    label/.style={rectangle, draw=none, align=center, thin},
    point/.style={circle, fill=black, thin, minimum width=.05cm}
}

\begin{tikzpicture}
    \node[square] (stackbottom1) {3};
    \node[square, below=0cm of stackbottom1] (stacktop1) {5};
    \node[label, above=.2cm of stackbottom1] (labelstack1) {Initial};

    \node[square, right=2cm of stackbottom1] (stackbottom2) {3};
    \node[square, below=0cm of stackbottom2] (stackmiddle2) {5};
    \node[square, below=0cm of stackmiddle2] (stacktop2) {2};
    \node[label, above=.2cm of stackbottom2] (labelstack2) {After push};

    \node[square, right=2cm of stackbottom2] (stackbottom3) {3};
    \node[square, below=0cm of stackbottom3] (stacktop3) {5};
    \node[square, dotted, below=0cm of stacktop3] (stackpopped) {2};
    \node[label, above=.2cm of stackbottom3] (labelstack3) {After pop};

    \node[square, right=2cm of stackbottom3] (stackbottom4) {3};
    \node[square, below=0cm of stackbottom4] (stacktop4) {5};
    \node[label, above=.2cm of stackbottom4] (labelstack4) {After top};

    \node[square, right=2cm of stackbottom4] (stackbottom5) {3};
    \node[square, below=0cm of stackbottom5] (stacktop5) {7};
    \node[label, above=.2cm of stackbottom5] (labelstack5) {After set};

    \node[square, dotted, below right=1cm and 1cm of stacktop1] (push) {2};
    \node[label, below=.2cm of push] (pushlabel) {push};

    \node[square, right=2cm of push] (pop) {2};
    \node[label, below=.2cm of pop] (poplabel) {pop};

    \node[square, right=2cm of pop] (top) {5};
    \node[label, below=.2cm of top] (poplabel) {top};

    \node[square, dotted, right=2cm of top] (set) {7};
    \node[label, below=.2cm of set] (setlabel) {set};

    \path [thick, black, dashed, ->]
    (push.east) edge [bend right] (stacktop2.south)
    (stackpopped.south) edge [bend left] (pop.east)
    (stacktop4.south) edge [bend left] (top.east)
    (set.east) edge [bend right] (stacktop5.south)
    ;
\end{tikzpicture}

## Stack machine example: Postfix (Reverse Polish) notation

* Use a stack to compute expressions without the need for parentheses
* Evaluate expression from left to right, and when we encounter an:
    - Operand: We push it to the stack
    - Operator: We pop two operands from the stack, apply the operator and push
      the result back on the stack

### Example: `(4 - 2) / 2`

* In postfix notation it's: `4 2 - 2 /`
* Note: The stack grows downward

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    label/.style={rectangle, draw=black, align=center, thin},
    point/.style={circle, draw=black, thin, minimum width=.1cm}
}

\begin{tikzpicture}
    \node[value] (value1) {4};
    \node[value, right=1cm of value1] (value2) {2};
    \node[value, right=1cm of value2] (value3) {-};
    \node[value, right=1cm of value3] (value4) {2};
    \node[value, right=1cm of value4] (value5) {/};

    \node[square, below=.5cm of value2] (stack1) {4};
    \node[square, below=.5cm of value3, text width=.3cm] (stack2) {4 2};
    \node[square, below=.5cm of value4, text width=.3cm] (stack2) {2};
    \node[square, below=.5cm of value5, text width=.3cm] (stack3) {2 2};
    \node[square, below right=.7cm and 1cm of value5, text width=.3cm] (stack4) {1};

    \node[label, left=.5cm of value1] (input) {Input};
    \node[label, below=.8cm of input] (stack) {Stack};

    \node[point, below left=.25cm and .2cm of input] (pointleft) {};
    \node[point, right=12cm of pointleft] (pointright) {};

    \path [thin, black, ->]
    (pointleft.east) edge (pointright.west);
\end{tikzpicture}

## Python arithmetic expression

The expression `(4 - 2) / 2` is evaluated the same way in Python!

::: columns

:::: column

### Source code

```python
def example_expr(two, four):
    return (four - two) / two
```

::::

:::: column

### Bytecode

\scriptsize
```
 0 LOAD_FAST           1 (four)
 2 LOAD_FAST           0 (two)
 4 BINARY_SUBTRACT
 6 LOAD_FAST           0 (two)
 8 BINARY_TRUE_DIVIDE
10 RETURN_VALUE
```

::::

:::

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    label/.style={rectangle, draw=black, align=center, thin},
    point/.style={circle, draw=black, thin, minimum width=.1cm}
}

\begin{tikzpicture}
    \node[value] (value1) {4};
    \node[value, right=1cm of value1] (value2) {2};
    \node[value, right=1cm of value2] (value3) {-};
    \node[value, right=1cm of value3] (value4) {2};
    \node[value, right=1cm of value4] (value5) {/};

    \node[square, below=.5cm of value2] (stack1) {4};
    \node[square, below=.5cm of value3, text width=.3cm] (stack2) {4 2};
    \node[square, below=.5cm of value4, text width=.3cm] (stack2) {2};
    \node[square, below=.5cm of value5, text width=.3cm] (stack3) {2 2};
    \node[square, below right=.7cm and 1cm of value5, text width=.3cm] (stack4) {1};

    \node[label, left=.5cm of value1] (input) {Input};
    \node[label, below=.8cm of input] (stack) {Stack};

    \node[point, below left=.25cm and .2cm of input] (pointleft) {};
    \node[point, right=12cm of pointleft] (pointright) {};

    \path [thin, black, ->]
    (pointleft.east) edge (pointright.west);
\end{tikzpicture}

## BINARY_SUBTRACT evaluation

```c
case TARGET(BINARY_SUBTRACT): {
    PyObject *right = POP();
    PyObject *left = TOP();
    PyObject *diff = PyNumber_Subtract(left, right);
    Py_DECREF(right);
    Py_DECREF(left);
    SET_TOP(diff);
    if (diff == NULL)
        goto error;
    DISPATCH();
}
```

## LOAD_FAST evaluation

```c
case TARGET(LOAD_FAST): {
    PyObject *value = GETLOCAL(oparg);
    if (value == NULL) {
        // [...]
        goto error;
    }
    Py_INCREF(value);
    PUSH(value);
    FAST_DISPATCH();
}
```


## BINARY_TRUE_DIVIDE evaluation

```c
case TARGET(BINARY_TRUE_DIVIDE): {
    PyObject *divisor = POP();
    PyObject *dividend = TOP();
    PyObject *quotient = PyNumber_TrueDivide(dividend, divisor);
    Py_DECREF(dividend);
    Py_DECREF(divisor);
    SET_TOP(quotient);
    if (quotient == NULL)
        goto error;
    DISPATCH();
}
```

# Memory management

## Question for the audience

\begin{minipage}{\linewidth}
\centering \huge How large is a Python `bool`?
\end{minipage}

## Everything is a `PyObject`

Every single value you can interact with in Python is wrapped in a `PyObject`
struct, which is typically 28 bytes or larger.

```python
# running Python 3.9
>>> sys.getsizeof(None)
16
>>> sys.getsizeof(True)
28
>>> sys.getsizeof(dict())
64
```

Takeaway: Python objects have _huge_ memory footprints, so we need efficient
disposal of unused objects.

## Reference counting

`PyObject`s have an internal count of the amount of references to that object, which is:

* Incremented when new references are created
* Decremented when references go out of scope
    - Out of scope ~ frame object is destroyed
    - When the count reaches 0, the object is destroyed

\small
Count increases with new references and decreases when references go out of scope

\scriptsize
```python
my_obj = object()   # ob_refcnt = 1
also_obj = my_obj   # ob_refcnt = 2
print(my_obj)       # ob_refcnt = 3, reference is stored in print's frame (locals)
                    # ob_refcnt = 2 after print returns, its frame being destroyed
```

## Cyclical references from exception handling

\centering If you catch an exception, you get a cyclical reference!

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    point/.style={circle, fill=black, thin, minimum width=.05cm}
}

\centering
\begin{tikzpicture}
    \node[square,label={main frame}, xshift=-7cm, minimum width=80, minimum height=125] (frameMain) {};

    \node[square, label={Locals}, yshift=1cm, xshift=-7cm] (localsMain) {\texttt{*exc}};

    \node[square, below=.6cm of localsMain] (backMain) {f\_back};

    \node[square, label={Code}, below=.6cm of backMain] (bytecodeMain) {
        \tiny \texttt{def main():}\\  ...
    };

    \node[square, label={create\_numbers frame}, minimum width=80, minimum height=125] (frameCreateNumbers) {};

    \node[square, label={Locals}, yshift=1cm] (localsCreateNumbers) {\texttt{*numbers}};

    \node[square, below=.6cm of localsCreateNumbers] (backCreateNumbers) {f\_back};

    \node[square, label={Code}, below=.6cm of backCreateNumbers] (bytecodeCreateNumbers) {
        \tiny \texttt{def create\_numbers():}\\  ...
    };

    \node[value, right=2cm of localsMain] (exception) {\texttt{exc}};
    \node[value, right=1cm of localsCreateNumbers] (numbers) {\texttt{numbers}};

    \path [thick, black, ->]
    (localsMain.east) edge (exception.west)
    (exception.east) edge (frameCreateNumbers.west)
    (backCreateNumbers.west) edge (frameMain.east)
    (localsCreateNumbers.east) edge (numbers.west)
    ;

\end{tikzpicture}

## Cyclical references from exception handling

\centering If you catch an exception, you get a cyclical reference!

\tikzset{
    square/.style={rectangle, draw=black, align=center, minimum width=5, thick},
    value/.style={circle, draw=black, align=center, thick, minimum width=20},
    point/.style={circle, fill=black, thin, minimum width=.05cm}
}

\centering
\begin{tikzpicture}
    \node[square,label={main frame}, xshift=-7cm, minimum width=80, minimum height=125] (frameMain) {};

    \node[square, label={Locals}, yshift=1cm, xshift=-7cm] (localsMain) {\texttt{*exc}};

    \node[square, below=.6cm of localsMain] (backMain) {f\_back};

    \node[square, label={Code}, below=.6cm of backMain] (bytecodeMain) {
        \tiny \texttt{def main():}\\  ...
    };

    \node[square, label={create\_numbers frame}, minimum width=80, minimum height=125] (frameCreateNumbers) {};

    \node[square, label={Locals}, yshift=1cm] (localsCreateNumbers) {\texttt{*numbers}\\\texttt{*exc}};

    \node[square, below=.4cm of localsCreateNumbers] (backCreateNumbers) {f\_back};

    \node[square, label={Code}, below=.6cm of backCreateNumbers] (bytecodeCreateNumbers) {
        \tiny \texttt{def create\_numbers():}\\  ...
    };

    \node[value, right=2cm of localsMain] (exception) {\texttt{exc}};
    \node[value, right=1cm of localsCreateNumbers] (numbers) {\texttt{numbers}};

    \path [thick, black, ->]
    (localsMain.east) edge (exception.west)
    (exception.east) edge (frameCreateNumbers.west)
    (backCreateNumbers.west) edge (frameMain.east)
    (localsCreateNumbers.east) edge (numbers.west)
    (localsCreateNumbers.west) edge [bend right] (exception.north)
    ;

\end{tikzpicture}

## Garbage collection

Reference counting does not work if there are cyclical references.

```python
def create_cyclical_reference():
    my_list = []
    my_list.append(my_list)
```

It is the job of the garbage collector (GC) to find and dispose of objects that
are _unreachable_ from the running program.

# Closing words

## Recap

* Python is compiled and interpreted
    - Compiling a program before hand makes startup faster
    - Although to be completely honest I've never, ever, ever done that :)
* Python's interpreter is a stack machine
    - Actually that's not all that useful to know unless you work on the interpreter
    - But great inspiration if you want to create a programming language of your own!
* Python's memory management: reference counting and garbage collection
    - Make sure variables with large amounts of data go out of scope ASAP
    - Cyclical references requires garbage collection (runs automatically)

## Want to learn more?

* I learned most of this from the book _CPython Internals_ [@cpython_internals]
    - Great book, highly recommend it
    - The author also made a blog post with a (much) shorter overview of the same thing [@cpython_guide]
* The official developer guide contains a lot of good info on how to work with
  CPython [@cpython_dev_guide]

## References{.allowframebreaks}
