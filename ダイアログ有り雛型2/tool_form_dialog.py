# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Tool Form sample
        copyright            : (C) 2022 by Chiakikun
        email                : chiakikungm@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.Qt import pyqtSignal, QApplication, QCursor, QTextCursor

import os
import configparser
import time

from qgis.core import *
from qgis.gui  import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'tool_form.ui'))

class ToolFormDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, iface, action, parent=None):
        super(ToolFormDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = action

        self.iniFile = os.path.dirname(__file__)+'/toolform_sample.ini'


    def showEvent(self, e):
        self.setModal(True)
        self.loadIni()

        # ポイントレイヤ選択 ということで、選択可能なレイヤのタイプをポイントに制限する
        self.mMapLayerComboBox_selectPoint.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBox_selectPoint.layerChanged.connect(self.onChangeLayer)
        self.onChangeLayer(self.mMapLayerComboBox_selectPoint.layer(0))


    def closeEvent(self, e):
        self.saveIni()

        self.mMapLayerComboBox_selectPoint.layerChanged.disconnect(self.onChangeLayer)


    def click_pushButton_cancel(self):
        self.calc.isStop = True


    def click_pushButton_close(self):
        self.close()


    def click_pushButton_exec(self):
        self.calc = Execute([])
        self.calc.log.connect(self.onLog)
        self.calc.finish.connect(self.onQuit)
        self.calc.progress.connect(self.onProgress)
        self.progressBar.setMaximum(self.calc.maxProcess)

        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        self.enableControls(False)
        self.calc.start()

    
    def click_toolButton_directory(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None, '', '')
        if path == '':
            return
        self.lineEdit_directory.setText(path)


    def click_toolButton_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None, '', '', 'Text File (*.txt)')[0]
        if path == '':
            return
        self.lineEdit_file.setText(path)


    def click_toolButton_save(self):
        path = QtWidgets.QFileDialog.getSaveFileName(None, '', '', 'Text File (*.txt)')[0]
        if path == '':
            return
        with open(path, 'w') as logfile:
            logfile.write(str(self.textEdit_log.toPlainText()))


    def click_toolButton_copy(self):
        c = self.textEdit_log.textCursor()
        self.textEdit_log.selectAll()
        self.textEdit_log.copy()
        self.textEdit_log.setTextCursor(c)


    def click_toolButton_clear(self):
        self.textEdit_log.clear()


    def enableControls(self, flag):
        self.tabWidget.setEnabled(flag)
        self.pushButton_exec.setEnabled(flag)
        self.pushButton_close.setEnabled(flag)
        self.pushButton_cancel.setEnabled(not flag)

        if flag:
            QApplication.restoreOverrideCursor()
        else:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.progressBar.setValue(0)


    def log(self, msg):
        self.textEdit_log.moveCursor(QTextCursor.End)
        self.textEdit_log.insertPlainText(msg)


    def loadIni(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.iniFile)
        if not self.config.has_section('sample'):
            try:
                self.lineEdit_file.setText(self.config['sample']['ファイル名'])
            except:
                self.lineEdit_file.setText('')

            try:
                self.lineEdit_directory.setText(self.config['sample']['フォルダ名'])
            except:
                self.lineEdit_directory.setText('')
 

    def saveIni(self):
        if not self.config.has_section('sample'):
            self.config.add_section('sample')

        self.config['sample']['ファイル名'] = self.lineEdit_file.text()
        self.config['sample']['フォルダ名'] = self.lineEdit_directory.text()

        with open(self.iniFile, 'w') as configfile:
            self.config.write(configfile)


    def onChangeLayer(self, layer):
        self.mFieldComboBox.setLayer(layer)
        self.mFieldComboBox.setCurrentIndex(0)


    def onLog(self, value):
        self.log(value)


    def onQuit(self):
        self.textEdit_log.append('終了\n')
        self.enableControls(True)


    def onProgress(self, value):
        self.progressBar.setValue(value)


class Execute(QThread):
    log = pyqtSignal(str)
    finish = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, args, parent=None):
        super(Execute, self).__init__(parent)
        self.__args = args

        self.isStop = False
        self.maxProcess = 1000


    def run(self):
        self.log.emit("実行します...\n")

        for i in range(0, self.maxProcess):
            time.sleep(0.01)
            if self.isStop:                        
                self.log.emit("中止しました\n")
                self.finish.emit()
                return
            self.progress.emit(i)

        self.finish.emit()