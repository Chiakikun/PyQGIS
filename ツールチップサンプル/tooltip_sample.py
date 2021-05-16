# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToolTipSample
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
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *

from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QToolTip

class ToolTipSample(QgsMapTool):

    def start(self):
        maptool = ToolTipClass(self.canvas, 100)

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'ツールチップサンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, ToolTipSample):
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


class ToolTipClass(QgsMapTool):

    def __init__(self, canvas, ms): # msはミリ秒
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas

        self.ms = ms
        # canvasMoveEventで設定した秒数（msで設定）経過したら呼ばれるメソッドを設定
        self.timerMapTips = QTimer( canvas )
        self.timerMapTips.timeout.connect( self.showMapTip )


    def canvasMoveEvent(self, event):
        QToolTip.hideText()
        self.timerMapTips.start(self.ms)


    def showMapTip( self ):
        self.timerMapTips.stop()

        # 表示する値を設定する。
        mappos = self.toMapCoordinates(self.canvas.mouseLastXY())
        value = mappos

        if value == None:
            return
        text = str(value)
        QToolTip.showText( self.canvas.mapToGlobal( self.canvas.mouseLastXY() ), text, self.canvas )


    def deactivate(self):
        self.timerMapTips.timeout.disconnect( self.showMapTip )
