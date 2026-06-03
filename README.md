cd /Users/janeshwarchowdhary/Desktop/g
python3 -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload

cd /Users/janeshwarchowdhary/Desktop/g
PYTHONPATH=. streamlit run app/app.py

PS C:\Users\jchowdha\Desktop\g>  & 'c:\Users\jchowdha\Desktop\g\.venv\Scripts\python.exe' 'c:\Users\jchowdha\.vscode\extensions\ms-python.debugpy-2026.6.0-win32-x64\bundled\libs\debugpy\launcher' '51171' '--' '-m' 'uvicorn' 'app.routes:app' '--host' '127.0.0.1' '--port' '8000' '--reload' 
Traceback (most recent call last):
  File "C:\Program Files\Python314\Lib\runpy.py", line 198, in _run_module_as_main
    return _run_code(code, main_globals, None,
                     "__main__", mod_spec)
  File "C:\Program Files\Python314\Lib\runpy.py", line 88, in _run_code
    exec(code, run_globals)
    ~~~~^^^^^^^^^^^^^^^^^^^
  File "c:\Users\jchowdha\.vscode\extensions\ms-python.debugpy-2026.6.0-win32-x64\bundled\libs\debugpy\launcher/../..\debugpy\__main__.py", line 69, in <module>
    from debugpy.server import cli
  File "c:\Users\jchowdha\.vscode\extensions\ms-python.debugpy-2026.6.0-win32-x64\bundled\libs\debugpy\launcher/../..\debugpy/..\debugpy\server\cli.py", line 23, in <module>
    from debugpy.common import log, sockets
  File "c:\Users\jchowdha\.vscode\extensions\ms-python.debugpy-2026.6.0-win32-x64\bundled\libs\debugpy\launcher/../..\debugpy/..\debugpy\common\log.py", line 375, in <module>
    stderr = LogFile(
        "<stderr>",
    ...<2 lines>...
        close_file=False,
    )
  File "c:\Users\jchowdha\.vscode\extensions\ms-python.debugpy-2026.6.0-win32-x64\bundled\libs\debugpy\launcher/../..\debugpy/..\debugpy\common\log.py", line 57, in __init__
    platform.platform(),
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\Python314\Lib\platform.py", line 1354, in platform
    system, node, release, version, machine, processor = uname()
                                                         ~~~~~^^
  File "C:\Program Files\Python314\Lib\platform.py", line 1016, in uname
    release, version, csd, ptype = win32_ver()
                                   ~~~~~~~~~^^
  File "C:\Program Files\Python314\Lib\platform.py", line 467, in win32_ver
    version, csd, ptype, is_client = _win32_ver(version, csd, ptype)
                                     ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python314\Lib\platform.py", line 408, in _win32_ver
    (version, product_type, ptype, spmajor, spminor)  = _wmi_query(
                                                        ~~~~~~~~~~^
        'OS',
        ^^^^^
    ...<4 lines>...
        'ServicePackMinorVersion',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Program Files\Python314\Lib\platform.py", line 347, in _wmi_query
    data = _wmi.exec_query("SELECT {} FROM {}".format(
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        ",".join(keys),
        ^^^^^^^^^^^^^^^
        table,
        ^^^^^^
    )).split("\0")
    ^^
KeyboardInterrupt
