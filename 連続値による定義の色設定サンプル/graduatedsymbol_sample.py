# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GraduatedSymbolSample
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

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *

import time

class GraduatedSymbolSample(QgsMapTool):

    def start(self):
        maptool = self

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合

        self.layer = self.iface.activeLayer()

        # 元の設定を保存
        self.oldrenderer = self.layer.renderer().clone()

        # 設定
        rangelist = []
        for minv, maxv, color_name in self.rules:
            symbol = QgsSymbol.defaultSymbol(self.layer.geometryType())
            symbol.symbolLayer(0).setStrokeColor(QColor('transparent'))
            symbol.setColor(QColor(color_name))        
            rangelist.append( QgsRendererRange(minv, maxv, symbol, str(minv) +' - '+ str(maxv)) )

        self.renderer = QgsGraduatedSymbolRenderer(self.field, rangelist)
        self.renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        self.layer.setRenderer(self.renderer)
        self.layer.triggerRepaint()


    def finish(self):
        # 元の設定に戻す
        self.layer.setRenderer(self.oldrenderer)
        self.layer.triggerRepaint()

        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = '連続値による定義の色設定サンプル' # プラグイン名
        self.menu_pos    = 'サンプル'           # プラグインの登録場所
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.field = '〇〇'

        # ルール
        self.rules = (
            (0,     30,   '#ffffff'),
            (30.1,  60,   '#ffcccc'),
            (60.1,  90,   '#ff9999'),
            (90.1,  120,  '#ff6666'),
            (120.1, 150,  '#ff3333'),
            (150.1, 9999, '#ff0000')
        )

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, GraduatedSymbolSample):
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
