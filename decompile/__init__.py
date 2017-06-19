import sys, types, os
import Scanner, Walker, verify, magics
def _load_file(filename):
    fp = open(filename, 'rb')
    source = fp.read()+'\n'
    try:
        co = compile(source, filename, 'exec')
    except SyntaxError:
        print >> sys.stderr, '>>Syntax error in', filename
        raise
    fp.close()
    return co
def _load_module(filename):
    import magics, marshal_files
    fp = open(filename, 'r')
    magic = fp.read(4)
    try:
        version = magics.versions[magic]
        marshal = marshal_files.import_(magic=magic)
    except KeyError:
        raise ImportError, "Unknown magic number in %s" % filename
    fp.read(4)
    co = marshal.load(fp)
    fp.close()
    return version, co
def decompyle(version, co, out=None, showasm=0, showast=0):
    assert type(co) == types.CodeType
    __real_out = out or sys.stdout
    scanner = Scanner.getscanner(version)
    scanner.setShowAsm(showasm, out)
    tokens, customize = scanner.disassemble(co)
    walker = Walker.Walker(out, scanner, showast=showast)
    try:
        ast = walker.build_ast(tokens, customize)
    except Walker.ParserError, e :
        print >>__real_out, e
        raise
    del tokens
    assert ast == 'stmts'
    if ast[0] == Walker.ASSIGN_DOC_STRING(co.co_consts[0]):
        walker.print_docstring('', co.co_consts[0])
        del ast[0]
    if ast[-1] == Walker.RETURN_NONE:
        ast.pop()
    walker.gen_source(ast, customize)
def decompyle_file(filename, outstream=None, showasm=0, showast=0):
    version, co = _load_module(filename)
    decompyle(version, co, out=outstream, showasm=showasm, showast=showast)
    co = None
if sys.platform.startswith('linux') and os.uname()[2][:2] == '2.':
    def __memUsage():
        mi = open('/proc/self/stat', 'r')
        mu = mi.readline().split()[22]
        mi.close()
        return int(mu) / 1000000
else:
    def __memUsage():
        return ''
def main(in_base, out_base, files, outfile=None,
         showasm=0, showast=0, do_verify=0):
    def _get_outstream(outfile):
        dir = os.path.dirname(outfile)
        failed_file = outfile + '_failed'
        if os.path.exists(failed_file): os.remove(failed_file)
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except:
                raise "Can't create output dir '%s'" % dir
        return open(outfile, 'w')
    of = outfile
    tot_files = okay_files = failed_files = verify_failed_files = 0
    for file in files:
        infile = os.path.join(in_base, file)
        if of:
            outstream = _get_outstream(outfile)
        elif out_base is None:
            outstream = sys.stdout
        else:
            outfile = os.path.join(out_base, file) + '_dis'
            outstream = _get_outstream(outfile)
        try:
            decompyle_file(infile, outstream, showasm, showast)
            tot_files += 1
        except KeyboardInterrupt:
            if outfile:
                outstream.close()
                os.remove(outfile)
            raise
        except:
	    failed_files += 1
            sys.stderr.write("### Can't decompyle  %s\n" % file)
            if outfile:
                outstream.close()
                os.rename(outfile, outfile + '_failed')
            raise
	else:
            if outfile:
                outstream.close()
            if do_verify:
                try:
                    verify.compare_code_with_srcfile(infile, outfile)
                    print "+++ okay decompyling", infile, __memUsage()
                    okay_files += 1
                except verify.VerifyCmpError, e:
		    verify_failed_files += 1
                    os.rename(outfile, outfile + '_unverified')
                    print >>sys.stderr, "### Error Verifiying", file
                    print >>sys.stderr, e
            else:
                okay_files += 1
                print "+++ okay decompyling", infile, __memUsage()
    print 'decompyled %i files: %i okay, %i failed, %i verify failed' % \
          (tot_files, okay_files, failed_files, verify_failed_files)
