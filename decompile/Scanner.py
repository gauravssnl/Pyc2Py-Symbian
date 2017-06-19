__all__ = ['Token', 'Scanner', 'getscanner']
import types
class Token:
    def __init__(self, type, attr=None, pattr=None, offset=-1):
        self.type = intern(type)
        self.attr = attr
        self.pattr = pattr
        self.offset = offset
        
    def __cmp__(self, o):
        if isinstance(o, Token):
            return cmp(self.type, o.type) or cmp(self.pattr, o.pattr)
        else:
            return cmp(self.type, o)
    def __repr__(self):		return str(self.type)
    def __str__(self):
        pattr = self.pattr or ''
        return '%s\t%-17s %r' % (self.offset, self.type, pattr)
    def __hash__(self):		return hash(self.type)
    def __getitem__(self, i):	raise IndexError
class Code:
    def __init__(self, co, scanner):
        for i in dir(co):
            if i.startswith('co_'):
                setattr(self, i, getattr(co, i))
        self._tokens, self._customize = scanner.disassemble(co)
class Scanner:
    def __init__(self, version):
        self.__version = version
        import dis_files
        self.dis = dis_files.by_version[version]
        self.resetTokenClass()
        dis = self.dis
        self.JUMP_OPs = map(lambda op: dis.opname[op],
                            dis.hasjrel + dis.hasjabs)
    def setShowAsm(self, showasm, out=None):
        self.showasm = showasm
        self.out = out
    def setTokenClass(self, tokenClass):
        assert type(tokenClass) == types.ClassType
        self.Token = tokenClass
    def resetTokenClass(self):
        self.setTokenClass(Token)
    def disassemble(self, co):
        rv = []
        customize = {}
        dis = self.dis
        Token = self.Token
        code = co.co_code
        cf = self.find_jump_targets(code)
        n = len(code)
        i = 0
        extended_arg = 0
        free = None
        while i < n:
            offset = i
            if cf.has_key(offset):
                for j in range(cf[offset]):
                    rv.append(Token('COME_FROM',
                                    offset="%s_%d" % (offset, j) ))
            c = code[i]
            op = ord(c)
            opname = dis.opname[op]
            i += 1
            oparg = None; pattr = None
            if op >= dis.HAVE_ARGUMENT:
                oparg = ord(code[i]) + ord(code[i+1]) * 256 + extended_arg
                extended_arg = 0
                i += 2
                if op == dis.EXTENDED_ARG:
                    extended_arg = oparg * 65536L
                if op in dis.hasconst:
                    const = co.co_consts[oparg]
                    if type(const) == types.CodeType:
                        oparg = const
                        if const.co_name == '<lambda>':
                            assert opname == 'LOAD_CONST'
                            opname = 'LOAD_LAMBDA'
                        pattr = 'code_object ' + const.co_name
                    else:
                        pattr = const
                elif op in dis.hasname:
                    pattr = co.co_names[oparg]
                elif op in dis.hasjrel:
                    pattr = repr(i + oparg)
                elif op in dis.hasjabs:
                    pattr = repr(oparg)
                elif op in dis.haslocal:
                    pattr = co.co_varnames[oparg]
                elif op in dis.hascompare:
                    pattr = dis.cmp_op[oparg]
                elif op in dis.hasfree:
                    if free is None:
                        free = co.co_cellvars + co.co_freevars
                    pattr = free[oparg]
            if opname == 'SET_LINENO':
                continue
            elif opname in ('BUILD_LIST', 'BUILD_TUPLE', 'BUILD_SLICE',
                            'UNPACK_LIST', 'UNPACK_TUPLE', 'UNPACK_SEQUENCE',
                            'MAKE_FUNCTION', 'CALL_FUNCTION', 'MAKE_CLOSURE',
                            'CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW',
                            'CALL_FUNCTION_VAR_KW', 'DUP_TOPX',
                            ):
                opname = '%s_%d' % (opname, oparg)
                customize[opname] = oparg
            rv.append(Token(opname, oparg, pattr, offset))
        if self.showasm:
            out = self.out
            for t in rv:
                print >>out, t
            print >>out
        return rv, customize
    def find_jump_targets(self, code):
        HAVE_ARGUMENT = self.dis.HAVE_ARGUMENT
        hasjrel = self.dis.hasjrel
        targets = {}
        n = len(code)
        i = 0
        while i < n:
            c = code[i]
            op = ord(c)
            i += 1
            if op >= HAVE_ARGUMENT:
                oparg = ord(code[i]) + ord(code[i+1]) * 256
                i += 2
                label = -1
                if op in hasjrel:
                    label = i + oparg
                if label >= 0:
                    targets[label] = targets.get(label, 0) + 1
        return targets
__scanners = {}
def getscanner(version):
    if not __scanners.has_key(version):
        __scanners[version] = Scanner(version)
    return __scanners[version]
