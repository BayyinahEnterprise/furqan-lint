"""Documented limitation: methods on classes defined inside a function
body are not collected.

The v0.3.2 nested-class fix (Finding 3) makes ``Outer.Inner.method``
visible to D24 and ``return_none_mismatch``. The same descent does
NOT apply to a class defined inside a function body, e.g.,::

    def factory():
        class Local:
            def method(self) -> int:
                if x:
                    return 1
                # missing return path - currently not flagged

The argument for keeping it this way: a class inside a function is
locally scoped, used as a private implementation detail (often a
returned closure-like object), and not part of the module's public
contract. D24 and ``return_none_mismatch`` exist to keep the public
contract honest; pinning the silent pass on local classes makes that
choice explicit.

The argument for fixing it: a missing-return-path inside a local
class's method is still a real bug at runtime. If a future fixture
demonstrates a real regression caused by this, the fix is to extend
``_extract_calls`` / the function walker to also descend into nested
``ClassDef``-inside-``FunctionDef`` and collect their methods. For
now: pinned as deliberate.
"""


def factory():
    class Local:
        def method(self, x: int) -> int:
            if x > 0:
                return 1
            # Missing return on x <= 0 - silent PASS today.

    return Local
