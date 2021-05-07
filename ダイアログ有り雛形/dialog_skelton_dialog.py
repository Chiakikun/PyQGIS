# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Dialog Skelton
        copyright            : (C) 2019 by Chiakikun
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
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

import os
import qgis.core

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog_skelton_dialog_base.ui'))


class DialogSkeltonDialog(QtWidgets.QDialog, FORM_CLASS):

    def setConnect(self):
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def disConnect(self):
        # 上手い方法が見つからなかった
        try:
          self.canvas.mapToolSet.disconnect(self.unsetTool)
        except:
          pass

    def unsetTool(self, tool):
        self.unset = True
        self.pushButton_Exec.setChecked(False)
        self.unset = False


    def __init__(self, iface, action, parent=None):
        super(DialogSkeltonDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = action


    def closeEvent(self, e):
        try:
            self.pushButton_Exec.setChecked(False)
        except:
            pass


    def pushClose(self):
        self.close()


    def pushExec(self, checked):
        if checked == True:
            self.previousMapTool = self.canvas.mapTool()   # 現在のマップツールを退避
            self.setConnect()
            self.pushButton_Exec.setText('実行中')
        else:
            self.pushButton_Exec.setText('実行')
            self.disConnect()

            # プラグイン実行中に他のマップツールを選択した場合、
            # ここを実行すると実行ボタン押下直前のマップツールが選択状態になってしまうので。
            if ('self.unset') in locals() and (not self.unset):
                self.canvas.setMapTool(self.previousMapTool)