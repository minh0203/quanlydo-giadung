import sys, os
from pathlib import Path
venv = Path(sys.executable).resolve().parent.parent
plugin = venv / 'Lib' / 'site-packages' / 'PyQt5' / 'Qt5' / 'plugins'
os.environ['QT_PLUGIN_PATH'] = str(plugin)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(plugin)
os.environ.setdefault('QT_QPA_PLATFORM', 'windows')
import ui.login
import inspect
with open('ui_debug.txt', 'w', encoding='utf-8') as f:
    f.write('ui.login file=' + repr(ui.login.__file__) + '\n')
    f.write('has Ui_LoginDialog=' + repr(hasattr(ui.login, 'Ui_LoginDialog')) + '\n')
    f.write('setupUi source=' + inspect.getsource(ui.login.Ui_LoginDialog.setupUi)[:800].replace('\n','\\n') + '\n')
