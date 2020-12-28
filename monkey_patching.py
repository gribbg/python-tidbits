"""
    Monkey patching helper routines
"""

import inspect
import hashlib


def assert_no_change(item, expected, verbose=False):
    """ Assert that source for item has not changed since expected was calculated.

        :param item:     anything that `inspect.getsource` can lookup
        :param expected: md5 of source code
        :param verbose:  True to output message even if OK
    """
    found = hashlib.md5(inspect.getsource(item).encode()).hexdigest()
    if found != expected:
        raise Exception('code appears to have changed to md5 %r--patching aborted' % expected)
    if verbose:
        print('%s.%s: no code change' % (getattr(item, '__module__', '?'), getattr(item, '__name__', '?')))


assert_no_change(inspect.getsource, '60cea7e2226b9eb4ab2d6a7f1353110d', verbose=True)


def patch_base(name, bases, namespace):
    """ Replace the base class methods with methods defined
        in the patch-class::

            class PatchClass(ParentClass,  metaclass=patch_base):
                def method_to_replace(self, ...):
                    ...
    """
    for k, v in namespace.items():
        if not k.startswith('__'):
            for base in bases:
                setattr(base, k, v)

    def do_not_instantiate(self, *args, **kwargs):
        raise TypeError('Do not instantiate patch class')
    namespace['__init__'] = do_not_instantiate
    return type(name, bases, namespace)


class ExampleBase:
    def one(self):
        print('%s: one' % type(self).__name__)

    def two(self):
        print('%s: two' % type(self).__name__)


class ExampleDerived(ExampleBase):
    def two(self):
        print('%s: two-child' % type(self).__name__)


p = ExampleBase()
p.one()
p.two()
c = ExampleDerived()
c.one()
c.two()


class Patcher(ExampleBase, metaclass=patch_base):
    old_one = ExampleBase.one

    def one(self):
        print('%s: one-patched' % type(self).__name__)
        self.old_one()


print('after patch')
p.one()
p.two()
c.one()
c.two()

Patcher()       # This will raise a TypeError()
