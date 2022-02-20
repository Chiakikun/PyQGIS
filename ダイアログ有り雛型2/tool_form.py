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
from qgis.PyQt.QtCore import QPoint
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .tool_form_dialog import ToolFormDialog
import os.path

class ToolForm:

    def __init__(self, iface):
        self.plugin_name = 'ツール雛型' # プラグイン名
        self.menu_pos    = '雛型'              # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛型/ツール雛形」)
        self.toolbar     = True                # Trueならツールバーにアイコンを表示する
        self.checkable   = False               # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.first_start = True


    def initGui(self):
        icon = QIcon(os.path.dirname(__file__)+'/icon.png')
        self.action = QAction(icon, self.plugin_name, self.iface.mainWindow())
        self.action.triggered.connect(self.run)        # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(self.checkable)       # Trueだとアイコンを押下したら次に押下するまで凹んだままになる
        if self.toolbar:
            self.iface.addToolBarIcon(self.action)     # ツールバーにこのツールのアイコンを表示する
        self.iface.addPluginToMenu(self.menu_pos, self.action)


    # このプラグインを無効にしたときに呼ばれる
    def unload(self):
        self.iface.removePluginMenu(self.menu_pos, self.action)
        self.iface.removeToolBarIcon(self.action)


    # このツールのアイコンを押下したときに呼ばれる
    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = ToolFormDialog(self.iface, self.action, self.iface.mainWindow()) # self.iface.mainWindow()を渡すと、ダイアログがQGISの後ろに隠れないようになります

        # 邪魔にならない場所にダイアログを表示させたいので
        pos = self.canvas.mapToGlobal(QPoint( 0, 0 ))
        self.dlg.move(pos.x(), pos.y())

        self.dlg.show()
