Kohlrabi
--------

*Kohlrabi* is a asynchronous task queue for Python applications. It runs
on top of a Redis server, and fits in with any existing application that
runs on Python 3.3 or higher. It allows easy converting of parts of
applications to asyncio-compatible parts, without affecting any normal
blocking code.

Installation
~~~~~~~~~~~~

Kohlrabi is available on PyPI to install easily:

::

    pip install kohlrabi

Or, you can install it from GitHub directly:

::

    pip install https://github.com/SunDwarf/Kohlrabi.git@master

Usage
~~~~~

Kohlrabi comes in two parts - the client and the server.

A single object is shared by both sides, and should be defined in your
main file.

.. code:: python

        kh = kohlrabi.Kohlrabi()

When running the server, this object must be specified in a specific
format on the command line:

::

    kohlrabi-server yourapp.mainfile:kh

| The first part before the ``:`` represents the *import path* of the
  module; how you would load it if you were to import it. The second
  part represents the Kohlrabi object created previously.
| This will then load the Kohlrabi server, and load the tasks on the
  server-side.

In your app code, using Kohlrabi is incredibly simple.

Creating tasks
^^^^^^^^^^^^^^

To create a task, simply decorate a function with Kohlrabi task
decorator.

.. code:: python

        @kh.task
        def hello():
            print("Hello, world!")

Then, inside your main method (or ``__name__`` check), call the task as
if it was a function.

.. code:: python

        if __name__ == "__main__":
            hello()

If you check the console of the server process, it will have printed
``Hello, world!``.

More advanced tasks
^^^^^^^^^^^^^^^^^^^

An example of a more advanced task would be an addition task.

.. code:: python

        @kh.task
        def add(a, b):
            return a + b

Inside your main method, call the add task with the parameters chosen:

.. code:: python

        fut = add(1, 2)

This returns a ClientTaskResult object, which you can use to get the
result of the task.

.. code:: python

        print("Added together 1 and 2 to get:", fut.result)

Note that ``ClientTaskResult.result`` is blocking, and will wait until
the task has finished to get the result of the task. If you wish to only
wait a certain amount of time, use the
``ClientTaskResult.result_with_timeout`` method.

.. code:: python

        print("Added together 1 and 2 to get:", fut.result_with_timeout(1))

Chaining tasks
^^^^^^^^^^^^^^

If you wish to chain tasks together, use the ``yield from`` keywords. On
the server side, a task is just a wrapped coroutine, meaning you can use
it as if it was a coroutine.

.. code:: python

        @kh.task
        def add_two(a):
            return a + 2

        @kh.task
        def get_four():
            four = yield from add_two(2)
            return four
