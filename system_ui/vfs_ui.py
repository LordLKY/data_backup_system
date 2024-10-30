from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from file_system.virtual_file_system import VirtualFileSystem
from file_process.interface import *
import os
from pathlib import Path


'''VFS后端'''
# static class
class VFS_backend:
    vfs = None

    @staticmethod
    def init_vfs(dir: str, uid: str):
        VFS_backend.vfs = VirtualFileSystem(dir, uid)


'''固定基界面'''
# static class
class W_base:
    base_ui = None 
    
    @staticmethod
    def set_base_ui(base_ui):
        W_base.base_ui = base_ui

    @staticmethod
    def change_to_base():
        if W_base.base_ui is not None:
            W_base.base_ui.ui.show()


'''子界面1 - 设置界面'''
class W_1():
    def __init__(self, ui_path):
        self.ui = uic.loadUi(ui_path)
        self.ui.lineEdit1.textChanged.connect(self.b1_enable)
        self.ui.lineEdit2.textChanged.connect(self.b1_enable)
        self.ui.Button1.clicked.connect(self.b1_clicked)
    
    def b1_enable(self):
        if self.ui.lineEdit1.text() != '' and self.ui.lineEdit2.text() != '':
            self.ui.Button1.setEnabled(True)
        else:
            self.ui.Button1.setEnabled(False)
    
    def b1_clicked(self):
        dir = self.ui.lineEdit1.text()
        uid = self.ui.lineEdit2.text()
        VFS_backend.init_vfs(dir, uid)

        self.ui.lineEdit1.clear()
        self.ui.lineEdit2.clear()
        self.ui.Button1.setEnabled(False)
        self.ui.close()

        if VFS_backend.vfs is not None:
            W_base.base_ui.b_trigger()
        W_base.change_to_base()
    
    def show(self):
        self.ui.show()


'''子界面2/3 - 备份/恢复文件'''
class W_2_3():
    def __init__(self, ui_path, mode: str):
        self.mode = mode
        self.ui = uic.loadUi(ui_path)
        self.ui.Button1.clicked.connect(self.b1_clicked)
        self.ui.Button2.clicked.connect(self.b2_clicked)
        self.ui.lineEdit1.textChanged.connect(self.get_l1_text)
        self.ui.lineEdit2.textChanged.connect(self.get_l2_text)
# TODO:  确定checkBox的个数与对应类型
        self.ui.checkBox1.stateChanged.connect(self.get_cb_closure(self.ui.checkBox1))
        self.ui.checkBox2.stateChanged.connect(self.get_cb_closure(self.ui.checkBox2))
        self.ui.checkBox3.stateChanged.connect(self.get_cb_closure(self.ui.checkBox3))
        self.ui.checkBox4.stateChanged.connect(self.get_cb_closure(self.ui.checkBox4))
        self.ui.checkBox5.stateChanged.connect(self.get_cb_closure(self.ui.checkBox5))

        self.src_path = ''
        self.dst_path = ''
        self.type_filter = set()
        self.num_filter = 0
    
    def get_l1_text(self):
        self.src_path = self.ui.lineEdit1.text()

    def get_l2_text(self):
        self.dst_path = self.ui.lineEdit2.text()

    def get_cb_closure(self, cb):
        def get_cb_state():
            if cb.isChecked():
                self.num_filter += 1
                self.type_filter.add(cb.text())
            else:
                self.num_filter -= 1
                self.type_filter.discard(cb.text())
        return get_cb_state

    def b1_clicked(self):
        try:
            if self.mode == 'copy':
                if self.num_filter:
                    VFS_backend.vfs.copy_dir_from_outside_ex(self.src_path, self.dst_path, self.type_filter)
                else:
                    VFS_backend.vfs.copy_from_outside(self.src_path, self.dst_path)
            elif self.mode == 'recover':
                if self.num_filter:
                    VFS_backend.vfs.copy_dir_to_outside_ex(self.src_path, self.dst_path, self.type_filter)
                else:
                    VFS_backend.vfs.copy_to_outside(self.src_path, self.dst_path)
# TODO: 进一步处理各种Error
        except Exception as e:
            QMessageBox.about(QMainWindow(), 'Error', str(e))
    
    def b2_clicked(self):
        self.ui.lineEdit1.clear()
        self.ui.lineEdit2.clear()
        self.ui.checkBox1.setChecked(False)
        self.ui.checkBox2.setChecked(False)
        self.ui.checkBox3.setChecked(False)
        self.ui.checkBox4.setChecked(False)
        self.ui.checkBox5.setChecked(False)
        self.ui.close()
        self.src_path = ''
        self.dst_path = ''
        self.type_filter = set()
        self.num_filter = 0

        W_base.change_to_base()


'''子界面7 - 文件比对'''
class W_7():
    def __init__(self, ui_path):
        self.ui = uic.loadUi(ui_path)
        self.ui.Button1.clicked.connect(self.b1_clicked)
        self.ui.Button2.clicked.connect(self.b2_clicked)
        self.ui.lineEdit1.textChanged.connect(self.get_l1_text)
        self.ui.lineEdit2.textChanged.connect(self.get_l2_text)
        self.ui.textBrowser.append("文件夹2较文件夹1的不同为：\n")
        self.path1, self.path2 = '', ''
    
    def get_l1_text(self):
        self.path1 = self.ui.lineEdit1.text()

    def get_l2_text(self):
        self.path2 = self.ui.lineEdit2.text()
    
    def b1_clicked(self):
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append("文件夹2较文件夹1的不同为：\n")
        try:
            result = VFS_backend.vfs.compare_two_dir(self.path1, self.path2)
            self.ui.textBrowser.append(result)
        except Exception as e:
            QMessageBox.about(QMainWindow(), 'Error', str(e))
    
    def b2_clicked(self):
        self.ui.lineEdit1.clear()
        self.ui.lineEdit2.clear()
        self.path1, self.path2 = '', ''
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append("文件夹2较文件夹1的不同为：\n")
        self.ui.close()

        W_base.change_to_base()


'''子界面8 - 文件夹信息'''
class W_8():
    def __init__(self, ui_path):
        self.ui = uic.loadUi(ui_path)
        self.ui.Button1.clicked.connect(self.b1_clicked)
        self.ui.Button2.clicked.connect(self.b2_clicked)
        self.ui.lineEdit1.textChanged.connect(self.get_l1_text)
        self.ui.textBrowser.append("该目录内容为：\n")
        self.path = ''

    def get_l1_text(self):
        self.path = self.ui.lineEdit1.text()
    
    def b1_clicked(self):
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append("该目录内容为：\n")
        try:
            result = VFS_backend.vfs.get_dir_content(self.path)
            result = "\n".join(result)
            self.ui.textBrowser.append(result)
        except Exception as e:
            QMessageBox.about(QMainWindow(), 'Error', str(e))

    def b2_clicked(self):
        self.ui.lineEdit1.clear()
        self.path = ''
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append("该目录内容为：\n")
        self.ui.close()

        W_base.change_to_base()


'''子界面4/5/6 - 附加功能'''
class W_4_5_6():
    def __init__(self, ui_path, mode: str):
        self.mode = mode
        self.ui = uic.loadUi(ui_path)
        self.ui.Button1.clicked.connect(self.b1_clicked)
        self.ui.Button2.clicked.connect(self.b2_clicked)
        self.ui.Button3.clicked.connect(self.b3_clicked)
        self.ui.lineEdit1.textChanged.connect(self.get_l1_text)
        self.ui.lineEdit2.textChanged.connect(self.get_l2_text)

        self.text1, self.text2 = '', ''
        self.can_execute = True if self.mode != 'encrypt' else False
        self.ui.Button1.setEnabled(self.can_execute)
        self.ui.Button2.setEnabled(self.can_execute)
    
    def get_l1_text(self):
        self.text1 = self.ui.lineEdit1.text()

    def get_l2_text(self):
        self.text2 = self.ui.lineEdit2.text()

        if self.mode == 'encrypt':
            if len(self.text2) == 8:
                self.ui.Button1.setEnabled(True)
                self.ui.Button2.setEnabled(True)
            else:
                self.ui.Button1.setEnabled(False)
                self.ui.Button2.setEnabled(False)
    
    def b1_clicked(self):
        try:
            if self.mode == 'zip':
                fzip(self.text1, self.text2)
            elif self.mode == 'pack':
                fpack(self.text1, self.text2)
            elif self.mode == 'encrypt':
                fencrypt(self.text1, self.text2)
# TODO: 进一步处理各种Error
        except Exception as e:
            QMessageBox.about(QMainWindow(), 'Error', str(e))
    
    def b2_clicked(self):
        try:
            if self.mode == 'zip':
                funzip(self.text1, self.text2)
            elif self.mode == 'pack':
                funpack(self.text1, self.text2)
            elif self.mode == 'encrypt':
                fdecrypt(self.text1, self.text2)
# TODO: 进一步处理各种Error
        except Exception as e:
            QMessageBox.about(QMainWindow(), 'Error', str(e))
    
    def b3_clicked(self):
        self.ui.lineEdit1.clear()
        self.ui.lineEdit2.clear()
        self.ui.Button1.setEnabled(self.can_execute)
        self.ui.Button2.setEnabled(self.can_execute)
        self.ui.close()
        self.text1, self.text2 = '', ''

        W_base.change_to_base()


'''主界面'''
class VFS_ui:
    def __init__(self, ui_dir: Path):
        self.ui_dir = ui_dir
        self.ui = uic.loadUi(os.path.join(ui_dir, 'W_main.ui'))
        self.associate_sub_windows()

        self.ui.Button1.clicked.connect(self.b_clicked_closure(self.w1))
        self.ui.Button2.clicked.connect(self.b_clicked_closure(self.w2))
        self.ui.Button3.clicked.connect(self.b_clicked_closure(self.w3))
        self.ui.Button4.clicked.connect(self.b_clicked_closure(self.w4))
        self.ui.Button5.clicked.connect(self.b_clicked_closure(self.w5))
        self.ui.Button6.clicked.connect(self.b_clicked_closure(self.w6))
        self.ui.Button7.clicked.connect(self.b_clicked_closure(self.w7))
        self.ui.Button8.clicked.connect(self.b_clicked_closure(self.w8))
    
    def associate_sub_windows(self):
        W_base.set_base_ui(self)

        self.w1 = W_1(os.path.join(self.ui_dir, 'W_1.ui'))
        self.w2 = W_2_3(os.path.join(self.ui_dir, 'W_2.ui'), 'copy')
        self.w3 = W_2_3(os.path.join(self.ui_dir, 'W_3.ui'), 'recover')
        self.w4 = W_4_5_6(os.path.join(self.ui_dir, 'W_4.ui'), 'zip')
        self.w5 = W_4_5_6(os.path.join(self.ui_dir, 'W_5.ui'), 'pack')
        self.w6 = W_4_5_6(os.path.join(self.ui_dir, 'W_6.ui'), 'encrypt')
        self.w7 = W_7(os.path.join(self.ui_dir, 'W_7.ui'))
        self.w8 = W_8(os.path.join(self.ui_dir, 'W_8.ui'))
    
    def b_trigger(self):
        self.ui.Button2.setEnabled(True)
        self.ui.Button3.setEnabled(True)
        # self.ui.Button4.setEnabled(True)
        # self.ui.Button5.setEnabled(True)
        # self.ui.Button6.setEnabled(True)
        self.ui.Button7.setEnabled(True)
        self.ui.Button8.setEnabled(True)
    
    def b_clicked_closure(self, w):
        def b_clicked():
            self.ui.close()
            w.ui.show()
        return b_clicked
    
    def run(self):
        self.ui.show()
    
    def exit(self):
        # store all the changes before exit
        if VFS_backend.vfs is not None:
            VFS_backend.vfs.store_change()
