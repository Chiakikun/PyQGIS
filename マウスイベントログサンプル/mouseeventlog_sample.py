# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MouseEventLogSample
        copyright            : (C) 2020 by Chiakikun
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

from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *


class MouseEventLogSample(QgsMapTool):

    def start(self):
        maptool = MouseEventSample(self.canvas)

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'マウスイベントログサンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛形/ダイアログ無し雛形」)
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, MouseEventLogSample):
            self.finish()
            self.action.setChecked(False)


    def initGui(self):
        icon = QIcon(os.path.dirname(__file__)+'/icon.png')
        self.action = QAction(icon, self.plugin_name, self.iface.mainWindow())
        self.action.triggered.connect(self.execSample) # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(self.checkable)       # Trueだとアイコンを押下したら次に押下するまで凹んだままになる
        if self.toolbar:
            self.iface.addToolBarIcon(self.action)     # ツールバーにこのツールのアイコンを表示する
        self.iface.addPluginToMenu(self.menu_pos, self.action)
        

    # このプラグインを無効にしたときに呼ばれる
    def unload(self):
        self.iface.removePluginMenu(self.menu_pos, self.action)
        self.iface.removeToolBarIcon(self.action)


    # このツールのアイコンを押下したときに呼ばれる
    def execSample(self):
        if self.checkable:
            if self.action.isChecked(): # 凹状態になった
                self.previousMapTool = self.canvas.mapTool()  # 現在のマップツールを退避
                self.start()
            else:                       # 凸状態になった
                self.finish()
                self.canvas.setMapTool(self.previousMapTool)  # このツール実行前に戻す
        else:
            self.start()


class MouseEventSample(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)

    def canvasMoveEvent(self, event):
        print('マウス移動:' + str(self.toMapCoordinates(event.pos())))

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('左クリック!' + str(self.toMapCoordinates(event.pos())))

        if event.button() == Qt.RightButton:
            print('右クリック!' + str(self.toMapCoordinates(event.pos())))
