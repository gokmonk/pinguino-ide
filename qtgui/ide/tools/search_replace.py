#!/usr/bin/env python
#-*- coding: utf-8 -*-

from ..helpers.decorators import Decorator

########################################################################
class SearchReplace(object):
    """"""

    ##----------------------------------------------------------------------
    #def init_find(self):
        #self.connect(self.ventana.treeExamples, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QTreeWidgetItem*,int)")), self.openexample)
        #self.connect(self.ventana.pushButton_search, QtCore.SIGNAL(_fromUtf8("clicked()")), self.search)
        #self.connect(self.ventana.pushButton_prev, QtCore.SIGNAL(_fromUtf8("clicked()")), self.search_prev)
        #self.connect(self.ventana.pushButton_next, QtCore.SIGNAL(_fromUtf8("clicked()")), self.search_next)
        #self.connect(self.ventana.pushButton_replace, QtCore.SIGNAL(_fromUtf8("clicked()")), self.replace)
        #self.connect(self.ventana.pushButton_replaceall, QtCore.SIGNAL(_fromUtf8("clicked()")), self.replaceall) 
        #self.connect(self.ventana.lineEdit_search, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.searchInstantaneous)
        
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")  
    def search_instantaneous(self, text_to_search):
        editor = self.main.tabWidget_files.currentWidget()
        text_cur = editor.text_edit.textCursor()
        editor.text_edit.moveCursor(text_cur.Start)
        self.__search__(text_to_search)
        
        if self.main.checkBox_case_sensitive.isChecked():
            content = editor.text_edit.toPlainText()
            count = content.count(text_to_search)
            self.main.label_replace_info.setText("%d words were found."%count)
            
        else:
            content = editor.text_edit.toPlainText().lower()
            count = content.count(text_to_search.lower())
            self.main.label_replace_info.setText("%d words were found."%count)
        
    
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")  
    def __search__(self, text_to_search):
        self.find_match(word=text_to_search,
                        back=False,
                        sensitive=self.main.checkBox_case_sensitive.isChecked(),
                        whole=False)
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")  
    def search_previous(self):
        self.find_match(word=self.main.lineEdit_search.text(),
                        back=True,
                        sensitive=self.main.checkBox_case_sensitive.isChecked(),
                        whole=False)
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")    
    def search_next(self):
        self.find_match(word=self.main.lineEdit_search.text(),
                        back=False,
                        sensitive=self.main.checkBox_case_sensitive.isChecked(),
                        whole=False)  
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")
    @Decorator.requiere_line_edit_content("main.lineEdit_replace")
    def replace(self):
        editor = self.main.tabWidget_files.currentWidget()
        text_cur = editor.text_edit.textCursor()
        if text_cur.selectedText() == self.main.lineEdit_search.text():
            text_cur.removeSelectedText()
            text_cur.insertText(self.main.lineEdit_replace.text())
            text_cur.clearSelection()
            self.highligh_line(line=None, color="#ffff7f")
        
    #----------------------------------------------------------------------
    @Decorator.requiere_open_files()
    @Decorator.requiere_line_edit_content("main.lineEdit_search")
    @Decorator.requiere_line_edit_content("main.lineEdit_replace")
    def replaceall(self):
        self.replace_all_match(wordOld=self.main.lineEdit_search.text(),
                               wordNew=self.main.lineEdit_replace.text(),
                               sensitive=self.main.checkBox_case_sensitive.isChecked(),
                               whole=False)
        
    #----------------------------------------------------------------------
    def replace_all_match(self, wordOld, wordNew, sensitive=False, whole=False):
        editor = self.main.tabWidget_files.currentWidget()
        text_doc = editor.text_edit.document()
        text_cur = editor.text_edit.textCursor()
        s = text_doc.FindCaseSensitively if sensitive else None
        w = text_doc.FindWholeWords if whole else None
        editor.text_edit.moveCursor(text_cur.NoMove, text_cur.KeepAnchor)
        text_cur.beginEditBlock()
        editor.text_edit.moveCursor(text_cur.Start)
        count = 0
        while True:
            result = False
            if sensitive or whole: result = editor.text_edit.find(wordOld, s or w)
            else: result = editor.text_edit.find(wordOld)
            if result:
                tc = editor.text_edit.textCursor()
                if tc.hasSelection(): tc.insertText(wordNew)
                count += 1
            else: break
            #replace = False
        text_cur.endEditBlock()
        self.main.label_replace_info.setText("%d words were replaced."%count)

    #----------------------------------------------------------------------    
    def find_match(self, word, back, sensitive, whole):
        editor = self.main.tabWidget_files.currentWidget()
        text_doc = editor.text_edit.document()
        text_cur = editor.text_edit.textCursor()
        b = text_doc.FindBackward if back else None
        s = text_doc.FindCaseSensitively if sensitive else None
        w = text_doc.FindWholeWords if whole else None
        editor.text_edit.moveCursor(text_cur.NoMove, text_cur.KeepAnchor)
        if back or sensitive or whole: editor.text_edit.find(word, b or s or w)
        else:  editor.text_edit.find(word)
        self.highligh_line(line=None, color="#ffff7f", text_cursor=editor.text_edit.textCursor())
        
        
        