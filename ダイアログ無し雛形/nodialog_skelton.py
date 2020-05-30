# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NodialogSkelton
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

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis.core;

class NodialogSkelton(qgis.gui.QgsMapTool):

    def setConnect(self):
        maptool = self # 場合によって書き換えて

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def disConnect(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, NodialogSkelton):
            self.disConnect()
            self.action.setChecked(False)


    def __init__(self, iface):
        self.menu_pos = '雛形' # プラグインの登録場所
        self.plugin_name = 'ダイアログ無し雛形'
        self.toolbar = True

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        qgis.gui.QgsMapTool.__init__(self, self.canvas)


    def initGui(self):
        icon = QIcon(self.plugin_dir+'/icon.png')
        self.action = QAction(icon, self.plugin_name, self.iface.mainWindow())
        self.action.triggered.connect(self.execSample) # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(True)                 # Trueだとアイコンを押下したら次に押下するまで凹んだままになる
        if self.toolbar:
            self.iface.addToolBarIcon(self.action)     # ツールバーにこのツールのアイコンを表示する
        self.iface.addPluginToMenu(self.menu_pos, self.action)
        

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(self.menu_pos, self.action)
        self.iface.removeToolBarIcon(self.action)


    # このツールのアイコンを押下したとき
    def execSample(self):
        if self.action.isChecked(): # 凹状態になった
            self.previousMapTool = self.canvas.mapTool()  # 現在のマップツールを退避
            self.setConnect()
        else:                       # 凸状態になった
            self.disConnect()
            self.canvas.setMapTool(self.previousMapTool)  # このツール実行前に戻す
