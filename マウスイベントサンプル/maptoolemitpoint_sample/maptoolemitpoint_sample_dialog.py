# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapToolEmitPointSampleDialog
                                 A QGIS plugin
 MapToolEmitPointを使ったサンプルです。
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Chiakikun
        email                : chiakikungm@gmail.com
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
from qgis.PyQt import QtCore
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

import os
import qgis.core

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'maptoolemitpoint_sample_dialog_base.ui'))


class MapToolEmitPointSampleDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        super(MapToolEmitPointSampleDialog, self).__init__(parent)
        self.setupUi(self)

        self.canvas = iface.mapCanvas()
        # キャンバスウィンドウ上でのマウスイベントの設定
        self.mouseEventSample = qgis.gui.QgsMapToolEmitPoint(self.canvas)


    def unsetTool(self, tool):
        self.pushButton_Exec.setChecked(False)


    def closeEvent(self, e):
        try:
            self.pushButton_Exec.setChecked(False)
        except:
            pass

    def pushClose(self):
        self.close()


    def pushExec(self, checked):
        if checked == True:
            self.mouseEventSample.canvasClicked.connect(self.mouseClick)
            self.mouseEventSample.canvasMoveEvent = self.canvasMoveEvent        
            self.canvas.setMapTool(self.mouseEventSample)

            # このサンプル以外のアイコンを押した場合に、凹んでいる実行ボタンを元に戻すため
            self.canvas.mapToolSet.connect(self.unsetTool)
            self.pushButton_Exec.setText('実行中')
        else:
            self.pushButton_Exec.setText('実行')

            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)
            self.mouseEventSample.canvasClicked.disconnect(self.mouseClick)


    def canvasMoveEvent(self, event):
        print('マウス移動:' + str(self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())))

 
    def mouseClick(self, currentPos, clickedButton ):
        if clickedButton == QtCore.Qt.LeftButton: 
            print('左クリック!' + str(qgis.core.QgsPointXY(currentPos)))

        if clickedButton == QtCore.Qt.RightButton:
            print('右クリック!' + str(qgis.core.QgsPointXY(currentPos)))
