# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RelationSample
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
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *

from qgis.PyQt import QtWidgets

class RelationSample(QgsMapTool):

    def showChildren(self):
        parent = self.rel.referencedLayer()
        child = self.rel.referencingLayer()

        features = parent.selectedFeatures()
        if len(features) == 0:
            return

        child.removeSelection() # クリアしないと、属性テーブルに余計に表示されるから 
        for c in self.rel.getRelatedFeatures(features[0]):
            child.select(c.id())

        selectedlayer = self.iface.activeLayer() # 現在のアクティブレイヤ退避
        try:
            # このプログラム実行中は属性テーブルは選択中のフューチャーしか表示しないように設定する
            self.oldsetting = QSettings().value('/Qgis/attributeTableBehaviour')
            QSettings().setValue('/Qgis/attributeTableBehavior', 'ShowSelected')
            # テーブル表示
            self.iface.setActiveLayer(child)
            self.iface.mainWindow().findChild(QtWidgets.QAction, 'mActionOpenTable' ).trigger()
        finally:
            # 設定を戻す
            self.iface.setActiveLayer(selectedlayer)
            QSettings().setValue('/Qgis/attributeTableBehavior', self.oldsetting)


    def start(self):
        self.referencedLayer  = QgsProject.instance().mapLayersByName(self.referencedLayerName)[0]
        self.referencingLayer = QgsProject.instance().mapLayersByName(self.referencingLayerName)[0]
        self.rel = QgsRelation()

        self.rel.setReferencingLayer(self.referencingLayer.id())
        self.rel.setReferencedLayer(self.referencedLayer.id())
        self.rel.addFieldPair(self.referencingField, self.referencedField)
        self.rel.setId('適当なID')
        self.rel.setName('適当な名前')
        QgsProject.instance().relationManager().addRelation(self.rel)

        self.referencedLayer.selectionChanged.connect(self.showChildren)


    def finish(self):
        QgsProject.instance().relationManager().removeRelation(self.rel)
        self.referencedLayer.selectionChanged.disconnect(self.showChildren)


    def __init__(self, iface):
        self.plugin_name = 'リレーションサンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.referencedLayerName  = '〇〇〇' # 参照元のレイヤ名
        self.referencingLayerName = '□□□' # 参照先のレイヤ名
        self.referencedField  = '△△△'     # 参照先とのリンクに使うフィールド名
        self.referencingField = '×××'     # 参照元とのリンクに使うフィールド名

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, RelationSample):
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
