""" Pyc2Py.py by gauravssnl
It supports touchscreen device also as it uses powlite_fm_en mod translated to English by me """

import appuifw
import e32
import sys
import series60_console
import globalui
import py_compile
import py_decompile
try :
    import powlite_fm_en as powlite_fm
except :
    import powlite_fm
        
lock = e32.Ao_lock()
sleep = e32.ao_sleep
console = series60_console.Console()

def slow_print(text, end = "\n"):
    for c in str(text)+end :
        sys.stdout.write(c)
        sys.stdout.flush()
        sleep(0.3 / 90)

def app():
    global bd
    bd = console.text
    appuifw.app.body = bd
    appuifw.app.title = u"Pyc2Py v1.00"
    appuifw.app.exit_key_handler = lambda : appuifw.app.set_exit()
    bd.color = (255,0,255)
    bd.font = "title",20
    slow_print("pyc2py by gauravssnl")
    bd.color = (0,0,255)
    bd.font = "title",18
    slow_print("Features :")
    bd.color = (0,0,0)
    bd.font = "title",17
    slow_print("1.Decompile .pyc file to .py file")
    slow_print("2.Compile .py files to .pyc file")
    slow_print("*"*25)
    appuifw.app.menu = [(u"Decompile", decompile),(u"Compile", compile),(u"About",about)]
    
def decompile():
    manager = powlite_fm.manager()
    file = manager.AskUser(ext= [".pyc"])
    if file :
        slow_print("Decompiling File:")
        slow_print(file)
        py_decompile.decompile(file)
        slow_print("*"*25)
        
            
def compile():
    manager = powlite_fm.manager()
    file = manager.AskUser(ext= [".py"])
    if file :
        slow_print("Compiling File:")
        slow_print(file)
        py_compile.compile(file)
        slow_print("File has been compiled ")
        slow_print("*"*25)
    
def about():
 sleep(0.0001)
 globalui.global_msg_query(u"Decompiled files and compiled files are created in the same directory where your original file is located.Decompiled files are created with pyc_dis extension.",u"Pyc2Py by gauravssnl")
    


app()
lock.wait()    
              