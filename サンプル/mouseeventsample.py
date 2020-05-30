# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MouseEventSample
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
使い方例（『https://github.com/Chiakikun/PyQGIS/blob/master/ダイアログ無し雛形/nodialog_skelton.py』に組み込む場合）

このファイルをプラグインのフォルダに置く

インポート
from .mouseeventsample import MouseEventSample

setConnectの「maptool = self」を以下に書き換える
        maptool = MouseEventSample(self.canvas)
"""
import qgis.core
from qgis.PyQt import QtCore

class MouseEventSample(qgis.gui.QgsMapTool):
    def __init__(self, canvas):
        qgis.gui.QgsMapTool.__init__(self, canvas)

    def canvasMoveEvent(self, event):
        print('マウス移動:' + str(self.toMapCoordinates(event.pos())))

    def canvasPressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print('左クリック!' + str(self.toMapCoordinates(event.pos())))

        if event.button() == QtCore.Qt.RightButton:
            print('右クリック!' + str(self.toMapCoordinates(event.pos())))
