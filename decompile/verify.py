import types
import decompile, Scanner
JUMP_OPs = None
class VerifyCmpError(Exception):
	pass
class CmpErrorConsts(VerifyCmpError):
	def __init__(self, name, index):
		self.name = name
		self.index = index
	def __str__(self):
		return 'Compare Error within Consts of %s at index %i' % \
		       (repr(self.name), self.index)
class CmpErrorConstsLen(VerifyCmpError):
	def __init__(self, name, consts1, consts2):
		self.name = name
		self.consts = (consts1, consts2)
	def __str__(self):
		return 'Consts length differs in %s:\n\n%i:\t%s\n\n%i:\t%s\n\n' % \
		       (repr(self.name),
			len(self.consts[0]), `self.consts[0]`,
			len(self.consts[1]), `self.consts[1]`)
class CmpErrorCode(VerifyCmpError):
	def __init__(self, name, index, token1, token2):
		self.name = name
		self.index = index
		self.token1 = token1
		self.token2 = token2
	def __str__(self):
		return 'Code differs in %s at offset %i [%s] != [%s]' % \
		       (repr(self.name), self.index,
			repr(self.token1), repr(self.token2)) 
class CmpErrorCodeLen(VerifyCmpError):
	def __init__(self, name, tokens1, tokens2):
		self.name = name
		self.tokens = [tokens1, tokens2]
	def __str__(self):
		return reduce(lambda s,t: "%s%-37s\t%-37s\n" % (s, t[0], t[1]),
			      map(lambda a,b: (a,b),
				  self.tokens[0],
				  self.tokens[1]),
			      'Code len differs in %s\n' % str(self.name))
class CmpErrorMember(VerifyCmpError):
	def __init__(self, name, member, data1, data2):
		self.name = name
		self.member = member
		self.data = (data1, data2)
	def __str__(self):
		return 'Member %s differs in %s:\n\t%s\n\t%s\n' % \
		       (repr(self.member), repr(self.name),
			repr(self.data[0]), repr(self.data[1]))
__IGNORE_CODE_MEMBERS__ = ['co_filename', 'co_firstlineno', 'co_lnotab']
def cmp_code_objects(version, code_obj1, code_obj2, name=''):
	assert type(code_obj1) == types.CodeType
	assert type(code_obj2) == types.CodeType
	if isinstance(code_obj1, object):
		assert dir(code_obj1) == dir(code_obj2)
	else:
		assert dir(code_obj1) == code_obj1.__members__
		assert dir(code_obj2) == code_obj2.__members__
		assert code_obj1.__members__ == code_obj2.__members__
	if name == '__main__':
		name = code_obj1.co_name
	else:
		name = '%s.%s' % (name, code_obj1.co_name)
		if name == '.?': name = '__main__'
	if isinstance(code_obj1, object) and cmp(code_obj1, code_obj2):
		pass
	if isinstance(code_obj1, object):
		members = filter(lambda x: x.startswith('co_'), dir(code_obj1))
	else:
		members = dir(code_obj1);
	members.sort();
	tokens1 = None
	for member in members:
		if member in __IGNORE_CODE_MEMBERS__:
			pass
		elif member == 'co_code':
			scanner = Scanner.getscanner(version)
			scanner.setShowAsm( showasm=0 )
			global JUMP_OPs
			JUMP_OPs = scanner.JUMP_OPs
			scanner.setTokenClass(Token)
			try:
				tokens1,customize = scanner.disassemble(code_obj1)
				del customize
				tokens2,customize = scanner.disassemble(code_obj2)
				del customize
			finally:
				scanner.resetTokenClass()
			if len(tokens1) != len(tokens2):
				raise CmpErrorCodeLen(name, tokens1, tokens2)
			for i in xrange(len(tokens1)):
				if tokens1[i] != tokens2[i]:
					raise CmpErrorCode(name, i, tokens1[i],
							   tokens2[i])
			del tokens1, tokens2
		elif member == 'co_consts':
			if len(code_obj1.co_consts) != len(code_obj2.co_consts):
				raise CmpErrorConstsLen(name, code_obj1.co_consts ,code_obj2.co_consts)
			for idx in xrange(len(code_obj1.co_consts)):
				const1 = code_obj1.co_consts[idx]
				const2 = code_obj2.co_consts[idx]
				if type(const1) != type(const2):
					raise CmpErrorContType(name, idx)
				if type(const1) == types.CodeType:
					cmp_code_objects(version, const1,
							 const2, name=name)
				elif cmp(const1, const2) != 0:
					raise CmpErrorConsts(name, idx)
		else:
			if getattr(code_obj1, member) != getattr(code_obj2, member):
				raise CmpErrorMember(name, member,
						     getattr(code_obj1,member),
						     getattr(code_obj2,member))
class Token(Scanner.Token):
	def __cmp__(self, o):
		t = self.type
		if t in JUMP_OPs:
			return cmp(t, o.type)
		else:
			return cmp(t, o.type) \
			       or cmp(self.pattr, o.pattr)
	def __repr__(self):
		return '%s %s (%s)' % (str(self.type), str(self.attr),
				       repr(self.pattr))
def compare_code_with_srcfile(pyc_filename, src_filename):
	version, code_obj1 = decompile._load_module(pyc_filename)
	code_obj2 = decompile._load_file(src_filename)
	cmp_code_objects(version, code_obj1, code_obj2)
def compare_files(pyc_filename1, pyc_filename2):
	version, code_obj1 = decompile._load_module(pyc_filename1)
	version, code_obj2 = decompile._load_module(pyc_filename2)
	cmp_code_objects(version, code_obj1, code_obj2)
if __name__ == '__main__':
	t1 = Token('LOAD_CONST', None, 'code_object _expandLang', 52)
	t2 = Token('LOAD_CONST', -421, 'code_object _expandLang', 55)
	print `t1`
	print `t2`
	print cmp(t1, t2), cmp(t1.type, t2.type), cmp(t1.attr, t2.attr)
