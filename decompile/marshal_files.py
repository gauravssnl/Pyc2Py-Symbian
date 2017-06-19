import magics
__all__ = ['by_version', 'by_magic']
by_version = {
    '1.5': 'marshal_20',
    '1.6': 'marshal_20',
    '2.0': 'marshal_20',
    '2.1': 'marshal',
    '2.2': 'marshal',
    '2.3': 'marshal',
    }
by_magic = dict( [ (mag, by_version[ver])
                   for mag, ver in magics.versions.iteritems() ] )
def import_(module=None,version=None,magic=None):
    if module:    pass
    elif version: module = by_version[version]
    elif magic:   module = by_magic[magic]
    else:
        raise 'at least one argument is required'
    from __builtin__ import __import__
    if module == 'marshal':
        return __import__('marshal', globals(), locals())
    else:
        raise 'marshal_20 not found'
