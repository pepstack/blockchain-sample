#  https://stackoverflow.com/questions/13520421/recursive-dotdict
class attrdict(dict):
    """
    Attribute Dictionary.

    Enables getting/setting/deleting dictionary keys via attributes.
    Getting/deleting a non-existent key via attribute raises `AttributeError`.
    Objects are passed to `__convert` before `dict.__setitem__` is called.

    This class rebinds `__setattr__` to call `dict.__setitem__`. Attributes
    will not be set on the object, but will be added as keys to the dictionary.
    This prevents overwriting access to built-in attributes. Since we defined
    `__getattr__` but left `__getattribute__` alone, built-in attributes will
    be returned before `__getattr__` is called. Be careful::

        >>> a = attrdict()
        >>> a['key'] = 'value'
        >>> a.key
        'value'
        >>> a['keys'] = 'oops'
        >>> a.keys
        <built-in method keys of attrdict object at 0xabcdef123456>

        d = {
            "author": "zhangliang"
        }
        ad = attrdict(d)
        print d['author']
        print ad.author

    Use `'key' in a`, not `hasattr(a, 'key')`, as a consequence of the above.
    """
    def __init__(self, *args, **kwargs):
        # We trust the dict to init itself better than we can.
        dict.__init__(self, *args, **kwargs)
        # Because of that, we do duplicate work, but it's worth it.
        for k, v in self.iteritems():
            self.__setitem__(k, v)

    def __getattr__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            # Maintain consistent syntactical behaviour.
            raise AttributeError(
                "'attrdict' object has no attribute '" + str(k) + "'"
            )

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, attrdict.__convert(v))

    __setattr__ = __setitem__

    def __delattr__(self, k):
        try:
            dict.__delitem__(self, k)
        except KeyError:
            raise AttributeError(
                "'attrdict' object has no attribute '" + str(k) + "'"
            )

    @staticmethod
    def __convert(o):
        """
        Recursively convert `dict` objects in `dict`, `list`, `set`, and
        `tuple` objects to `attrdict` objects.
        """
        if isinstance(o, dict):
            o = attrdict(o)
        elif isinstance(o, list):
            o = list(attrdict.__convert(v) for v in o)
        elif isinstance(o, set):
            o = set(attrdict.__convert(v) for v in o)
        elif isinstance(o, tuple):
            o = tuple(attrdict.__convert(v) for v in o)
        return o