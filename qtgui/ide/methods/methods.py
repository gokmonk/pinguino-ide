#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import codecs

from PySide import QtGui, QtCore

from .decorators import Decorator
from .dialogs import Dialogs
from ..tools.files import Files
from ..tools.search_replace import SearchReplace
from ..methods.library_manager import Librarymanager


########################################################################
class Methods(SearchReplace):

    #----------------------------------------------------------------------
    #@Decorator.debug_time()
    def open_file_from_path(self, *args, **kwargs):
        filename = kwargs["filename"]
        if self.__check_duplicate_file__(filename): return

        self.update_recents(filename)

        if filename.endswith(".gpde"):
            self.switch_ide_mode(True)
            self.PinguinoKIT.open_file_from_path(filename=filename)
            return
        elif filename.endswith(".pde"):
            self.switch_ide_mode(False)
            
        
        self.new_file(filename=filename)
        editor = self.main.tabWidget_files.currentWidget()
        #pde_file = file(path, mode="r")
        pde_file = codecs.open(filename, "r", "utf-8")
        content = "".join(pde_file.readlines())
        pde_file.close()
        editor.text_edit.setPlainText(content)
        setattr(editor, "path", filename)
        self.main.tabWidget_files.setTabToolTip(self.main.tabWidget_files.currentIndex(), filename)
        self.main.tabWidget_files.setTabText(self.main.tabWidget_files.currentIndex(), os.path.split(filename)[1])       
        self.tab_changed()
        
        
        
    #----------------------------------------------------------------------
    @Decorator.call_later(100)
    #@Decorator.debug_time()
    def open_last_files(self):
        opens = self.configIDE.get_recents_open()
        
        if not opens: return
        
        files = "\n".join(opens)
        dialogtext = QtGui.QApplication.translate("Dialogs", "Do you want open files of last sesion?")
        if not Dialogs.confirm_message(self, dialogtext+"\n"+files):
            return
    
        self.setCursor(QtCore.Qt.WaitCursor)
        for file_ in opens:
            if os.path.exists(file_):
                self.open_file_from_path(filename=file_)
                #self.open_file_from_path_later(file_)
                
        self.main.actionSwitch_ide.setChecked(file_.endswith(".pdeg"))
        self.switch_ide_mode(file_.endswith(".pdeg"))
        self.setCursor(QtCore.Qt.ArrowCursor)
        
    ##----------------------------------------------------------------------
    #@Decorator.call_later(1)
    #@Decorator.degug_time()
    #def open_file_from_path_later(self, file_):
        #print "start: ",
        #print file_
        #self.open_file_from_path(filename=file_)
        #print "End: ",
        #print file_
        ##self.main.actionSwitch_ide.setChecked(file_.endswith(".pdeg"))
        ##self.switch_ide_mode(file_.endswith(".pdeg"))        
        
        

        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    def comment_uncomment(self):
        editor = self.main.tabWidget_files.currentWidget()
        cursor = editor.text_edit.textCursor()
        prevCursor = editor.text_edit.textCursor()
        
        text = cursor.selectedText()
        selected = bool(text)
        
        if text == "":  #no selected, single line
            start = editor.text_edit.document().findBlock(cursor.selectionStart()).firstLineNumber()
            startPosition = editor.text_edit.document().findBlockByLineNumber(start).position()    
            endPosition = editor.text_edit.document().findBlockByLineNumber(start+1).position() - 1        
            
            cursor.setPosition(startPosition)            
            cursor.setPosition(endPosition, QtGui.QTextCursor.KeepAnchor)
            editor.text_edit.setTextCursor(cursor)
            
        else:
            start = editor.text_edit.document().findBlock(cursor.selectionStart()).firstLineNumber()
            startPosition = editor.text_edit.document().findBlockByLineNumber(start).position()
            
            end = editor.text_edit.document().findBlock(cursor.selectionEnd()).firstLineNumber()            
            
            endPosition = editor.text_edit.document().findBlockByLineNumber(end+1).position() - 1        
            
            cursor.setPosition(startPosition)            
            cursor.setPosition(endPosition, QtGui.QTextCursor.KeepAnchor)
            editor.text_edit.setTextCursor(cursor)
            
            
        text = cursor.selectedText()
            
        lines = text.split(u'\u2029')
        firstLine = False
        for line in lines:
            if not line.isspace() and not line=="":
                firstLine = line
                break

        if firstLine != False:
            if firstLine.startswith("//"): self.uncommentregion()
            else: self.commentregion()
            
        if not selected:
            cursor.clearSelection()
            editor.text_edit.setTextCursor(prevCursor) 
            

    #----------------------------------------------------------------------
    def jump_to_line(self, line):
        self.highligh_line(line,  "#DBFFE3")
        
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_text_mode()
    def highligh_line(self, line=None, color="#ff0000", text_cursor=None):
        editor = self.main.tabWidget_files.currentWidget()
        
        if line:
            content = editor.text_edit.toPlainText()
            content = content.split("\n")[:line]
            position = len("\n".join(content))
            text_cur = editor.text_edit.textCursor()
            text_cur.setPosition(position)
            text_cur.clearSelection()
            editor.text_edit.setTextCursor(text_cur)
        else:
            text_cur = editor.text_edit.textCursor()
            text_doc = editor.text_edit.document()
            text_cur.clearSelection()
            editor.text_edit.setDocument(text_doc)
            editor.text_edit.setTextCursor(text_cur)            
            
        selection = QtGui.QTextEdit.ExtraSelection()
        selection.format.setBackground(QtGui.QColor(color))
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = editor.text_edit.textCursor()
        editor.text_edit.setExtraSelections([selection])
        selection.cursor.clearSelection()
        
        if text_cursor: editor.text_edit.setTextCursor(text_cursor)
        
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    def clear_highlighs(self):
        editor = self.main.tabWidget_files.currentWidget()
        editor.text_edit.setExtraSelections([])
    
    
    #----------------------------------------------------------------------
    def get_tab(self):
        if self.main.actionSwitch_ide.isChecked(): return self.main.tabWidget_graphical
        else: return self.main.tabWidget_files
        
            
    #----------------------------------------------------------------------
    def __update_path_files__(self, path):
        Files.update_path_files(path, self.main.listWidget_files, self.main.label_path)
        
        
    #----------------------------------------------------------------------
    def __update_graphical_path_files__(self, path):
        Files.update_path_files(path, self.main.listWidget_filesg, self.main.label_pathg)
        
        
    #----------------------------------------------------------------------
    def __update_current_dir_on_files__(self):
        tab = self.get_tab()
        if tab == self.main.tabWidget_files:
            if self.main.comboBox_files.currentText() == "Current file dir":
                editor = tab.currentWidget()
                dir_ = getattr(editor, "path", None)
                if dir_: self.__update_path_files__(os.path.split(dir_)[0])
                
        else:
            if self.main.comboBox_filesg.currentText() == "Current file dir":
                editor = tab.currentWidget()
                dir_ = getattr(editor, "path", None)
                if dir_: self.__update_graphical_path_files__(os.path.split(dir_)[0])
            
            
    #----------------------------------------------------------------------
    @Decorator.connect_features()
    def __save_file__(self, *args, **kwargs):
        editor = kwargs.get("editor", self.get_tab())
        content = editor.text_edit.toPlainText()
        #pde_file = file(editor.path, mode="w")
        pde_file = codecs.open(editor.path, "w", "utf-8")
        pde_file.write(content)
        pde_file.close()
        self.__text_saved__()
        
        
    #----------------------------------------------------------------------
    def __get_name__(self, ext=".pde"):
        index = 1
        name = "untitled-%d" % index + ext
        #filenames = [self.main.tabWidget_files.tabText(i) for i in range(self.main.tabWidget_files.count())]
        filenames = [self.get_tab().tabText(i) for i in range(self.get_tab().count())]
        while name in filenames or name + "*" in filenames:
            index += 1
            name = "untitled-%d" % index + ext
        return name + "*"
    
    
    #----------------------------------------------------------------------
    def __text_changed__(self, *args, **kwargs):
        index = self.main.tabWidget_files.currentIndex()
        filename = self.main.tabWidget_files.tabText(index)
        if not filename.endswith("*"):
            self.main.tabWidget_files.setTabText(index, filename+"*")
            self.main.actionSave_file.setEnabled(True)
        self.clear_highlighs()
            
    
    #----------------------------------------------------------------------
    def __text_saved__(self, *args, **kwargs):
        index = self.get_tab().currentIndex()
        filename = self.get_tab().tabText(index)
        if filename.endswith("*"):
            self.get_tab().setTabText(index, filename[:-1])
        self.main.actionSave_file.setEnabled(False)
        
        
    #----------------------------------------------------------------------
    def __text_can_undo__(self, *args, **kwargs):
        state = not self.main.actionUndo.isEnabled()
        self.main.actionUndo.setEnabled(state)
        editor = self.main.tabWidget_files.currentWidget()
        editor.tool_bar_state["undo"] = state
        
        
    #----------------------------------------------------------------------
    def __text_can_redo__(self, *args, **kwargs):
        state = not self.main.actionRedo.isEnabled()
        self.main.actionRedo.setEnabled(state)
        editor = self.main.tabWidget_files.currentWidget()
        editor.tool_bar_state["redo"] = state
        
        
    #----------------------------------------------------------------------
    def __text_can_copy__(self, *args, **kwargs):
        state = not self.main.actionCopy.isEnabled()
        self.main.actionCopy.setEnabled(state)
        self.main.actionCut.setEnabled(state)
        editor = self.main.tabWidget_files.currentWidget()
        editor.tool_bar_state["copy"] = state
        
        
    #----------------------------------------------------------------------
    def __check_duplicate_file__(self, filename):
        filenames = [getattr(self.get_tab().widget(i), "path", None) for i in range(self.get_tab().count())]
        if filename in filenames:
            Dialogs.file_duplicated(self, filename)
            self.get_tab().setCurrentIndex(filenames.index(filename))
            return True
        return False

                
    #----------------------------------------------------------------------
    def load_main_config(self):
        if self.configIDE.config("Main", "maximized", True):
            self.showMaximized()
        
        else:
            pos = self.configIDE.config("Main", "position", "(0, 0)")
            self.move(*eval(pos))
            
            size = self.configIDE.config("Main", "size", "(1050, 550)")
            self.resize(*eval(size))
        
        
    #----------------------------------------------------------------------
    def get_all_open_files(self):
        opens = []
        tab = self.main.tabWidget_files
        widgets = map(lambda index:tab.widget(index), range(tab.count()))
        for widget in widgets:
            path = getattr(widget, "path", False)
            if path: opens.append(path)
        tab = self.main.tabWidget_graphical
        widgets = map(lambda index:tab.widget(index), range(tab.count()))
        for widget in widgets:
            path = getattr(widget, "path", False)
            if path: opens.append(path)
        return opens
        

    #----------------------------------------------------------------------
    def update_recents(self, filename):
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.insert(0, filename)
        self.recent_files = self.recent_files[:10]
        
        self.update_recents_menu()
        
        
    #----------------------------------------------------------------------
    def update_recents_menu(self):
        self.main.menuRecents.clear()
        for file_ in self.recent_files:
            action = QtGui.QAction(self)
            filename = os.path.split(file_)[1]
            
            len_ = 40
            if len(file_) > len_:
                file_path_1 = file_[:len_/2]
                file_path_2 = file_[-len_/2:]
                file_path = file_path_1 + "..." + file_path_2
            else: file_path = file_
            
            if os.path.isfile(file_path):
                action.setText(filename+" ("+file_path+")")
                self.connect(action, QtCore.SIGNAL("triggered()"), self.menu_recent_event(file_))
                action.ActionEvent = self.menu_recent_event
                
                self.main.menuRecents.addAction(action)
        
        
    #----------------------------------------------------------------------
    def menu_recent_event(self, file_):
        def menu():
            self.open_file_from_path(filename=file_)
        return menu
            
            
    #----------------------------------------------------------------------
    def update_pinguino_paths(self):
        user_sdcc_bin = self.configIDE.get_path("sdcc_bin")
        if user_sdcc_bin: self.pinguinoAPI.P8_BIN = user_sdcc_bin
        
        user_gcc_bin = self.configIDE.get_path("gcc_bin")
        if user_gcc_bin: self.pinguinoAPI.P32_BIN = user_gcc_bin
        
        pinguino_source = os.path.join(os.getenv("PINGUINO_USER_PATH"), "source")
        if pinguino_source: self.pinguinoAPI.SOURCE_DIR = pinguino_source
        
        pinguino_8_libs = self.configIDE.get_path("pinguino_8_libs")
        if pinguino_8_libs: self.pinguinoAPI.P8_DIR = pinguino_8_libs
        
        pinguino_32_libs = self.configIDE.get_path("pinguino_32_libs")
        if pinguino_32_libs: self.pinguinoAPI.P32_DIR = pinguino_32_libs
                
                
    #----------------------------------------------------------------------
    def build_statusbar(self):
        self.status_info = QtGui.QLabel()
        self.main.statusBar.addPermanentWidget(self.status_info, 1)    
        
        
    #----------------------------------------------------------------------
    def update_namespaces(self):
        names = Namespaces()
        names.save_namespaces()        
        
        
    #----------------------------------------------------------------------
    def install_error_redirect(self):
        sys.stderr = Stderr
        sys.stderr.plainTextEdit_output = self.main.plainTextEdit_output


    #----------------------------------------------------------------------
    def output_ide(self, *args, **kwargs):
        for line in args:
            self.main.plainTextEdit_output.appendPlainText(line)
            
        for key in kwargs.keys():
            line = key + ": " + kwargs[key]
            self.main.plainTextEdit_output.appendPlainText(line)
        
        
    #----------------------------------------------------------------------
    def statusbar_ide(self, status):
        self.status_info.setText(status)
        
        
    #----------------------------------------------------------------------
    def set_board(self):
        board_name = self.configIDE.config("Board", "board", "Pinguino 2550")
        for board in self.pinguinoAPI._boards_:
            if board.name == board_name:
                self.pinguinoAPI.set_board(board)
        
        arch = self.configIDE.config("Board", "arch", 8)
        if arch == 8:
            bootloader = self.configIDE.config("Board", "bootloader", "v1_v2")
            if bootloader == "v1_v2":
                self.pinguinoAPI.set_bootloader(self.pinguinoAPI.Boot2)
            else:
                self.pinguinoAPI.set_bootloader(self.pinguinoAPI.Boot4)
                
        os.environ["PINGUINO_BOARD_ARCH"] = str(arch)
                
                
    #----------------------------------------------------------------------
    def get_description_board(self):
        board = self.pinguinoAPI.get_board()
        board_config = "Board: %s\n" % board.name
        board_config += "Proc: %s\n" % board.proc
        board_config += "Arch: %s\n" % board.arch
        
        if board.arch == 8 and board.bldr == "boot4":
            board_config += "Boootloader: v4\n"
        if board.arch == 8 and board.bldr == "boot2":
            board_config += "Boootloader: v1 & v2\n"
            
        return board_config
    
    
    #----------------------------------------------------------------------
    def get_status_board(self):
        self.set_board()
        board = self.pinguinoAPI.get_board()
        board_config = "Board: %s" % board.name
        
        if board.arch == 8 and board.bldr == "boot4":
            board_config += " - Boootloader: v4"
        if board.arch == 8 and board.bldr == "boot2":
            board_config += " - Boootloader: v1 & v2"
            
        return board_config
    
    
    #----------------------------------------------------------------------
    def update_user_libs(self):
        libs = Librarymanager()
        
        all_p8 = libs.get_p8_libraries()
        all_p8 = map(lambda lib:lib["p8"], all_p8)
        self.pinguinoAPI.USER_P8_LIBS = all_p8   
        
        all_p32 = libs.get_p32_libraries()
        all_p32 = map(lambda lib:lib["p8"], all_p32)
        self.pinguinoAPI.USER_P32_LIBS = all_p32  
        
        self.pinguinoAPI.USER_PDL = libs.get_pdls()