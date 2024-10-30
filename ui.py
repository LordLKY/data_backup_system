from system_ui.vfs_ui import VFS_ui
from PyQt5.QtWidgets import QApplication
from pathlib import Path

app = QApplication([])
vfs1 = VFS_ui(Path(__file__).parent / Path('UI'))
vfs1.run()
app.exec_()
vfs1.exit()
