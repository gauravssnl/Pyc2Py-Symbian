import magics
__all__ = ['by_version', 'by_magic']
_fallback = {
    'EXTENDED_ARG': None,
    'hasfree': [],
    }
class dis(object):
    def __init__(self, version, module):
        self._version = version
        from __builtin__ import __import__
        self._module = __import__('decompile.%s' % module, globals(),
                                  locals(), 'decompile')
    def __getattr__(self, attr):
        try:
            val = self._module.__dict__[attr]
        except KeyError, e:
            if _fallback.has_key(attr):
                val = _fallback[attr]
            else:
                raise e
        return val
by_version = {
    '1.5': dis('1.5', 'dis_15'),
    '1.6': dis('1.6', 'dis_16'),
    '2.0': dis('2.0', 'dis_20'),
    '2.1': dis('2.1', 'dis_21'),
    '2.2': dis('2.2', 'dis_22'),
    '2.3': dis('2.3', 'dis_23'),
    }
by_magic = dict( [ (mag, by_version[ver])
                   for mag, ver in magics.versions.iteritems() ] )
