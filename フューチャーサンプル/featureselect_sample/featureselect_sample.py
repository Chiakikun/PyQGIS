﻿# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FeatureSelectSample
                                 A QGIS plugin
 フューチャーをマウス選択するサンプルです
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-26
        git sha              : $Format:%H$
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
from qgis.PyQt.QtWidgets import QAction, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis.core;

class FeatureSelectSample:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # プラグインの登録場所
        self.menu_pos = 'サンプル フューチャー選択'
        # キャンバスウィンドウ上でのマウスイベントの設定
        self.mouseEventSample = FeatureSelectionTool(self.canvas)


    def initGui(self):
        icon = QIcon(self.plugin_dir+'/icon.png')
        self.action = QAction(icon, '一つ選択→属性編集', self.iface.mainWindow())
        self.action.triggered.connect(self.execSample) # アイコンを押下した時に実行されるメソッドを登録
        self.action.setCheckable(True)                 # Trueだとアイコンを押下したら次に押下するまで凹んだままになる。
        #self.iface.addToolBarIcon(self.action)         # ツールバーにアイコンを表示させたいなら#外して
        self.iface.addPluginToMenu(self.menu_pos, self.action)


    # このサンプル以外のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, FeatureSelectSample):
            try:
                self.mouseEventSample.featureIdentified.disconnect(self.editAttribute)
            except Exception:
                pass

            self.iface.layerTreeView().currentLayerChanged.disconnect(self.changeLayer)

            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)

            self.action.setChecked(False)


    def execSample(self):
        if self.action.isChecked():
            self.layer = self.iface.activeLayer()

            if (self.layer == None) or (type(self.layer) is not qgis._core.QgsVectorLayer):
                QMessageBox.about(None, '警告', 'ベクタレイヤを選択してから実行してください')
                self.action.setChecked(False)
                return

            self.previousMapTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.mouseEventSample)
            self.canvas.mapToolSet.connect(self.unsetTool)

            self.iface.layerTreeView().currentLayerChanged.connect(self.changeLayer) # アクティブレイヤが変更された時に呼ぶメソッドを登録
            self.mouseEventSample.setLayer(self.iface.activeLayer())
            self.mouseEventSample.featureIdentified.connect(self.editAttribute)
        else:
            self.mouseEventSample.featureIdentified.disconnect(self.editAttribute)
            self.iface.layerTreeView().currentLayerChanged.disconnect(self.changeLayer)
            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)
            self.canvas.setMapTool(self.previousMapTool)


    # フューチャーを一つ選択した時に呼ばれる。
    def editAttribute(self, feature):
        self.layer.removeSelection() 
        self.layer.select(feature.id()) 

        self.layer.startEditing() # レイヤを編集状態にする

        # 選択しているフューチャーの属性フォーム表示
        self.attdlg = self.iface.getFeatureForm(self.layer, feature)
        self.attdlg.setMode(qgis.gui.QgsAttributeEditorContext.SingleEditMode)
        self.attdlg.finished.connect(self.commitEdit)
        self.attdlg.show()


    def commitEdit(self, result):
        if result == 1:
            self.layer.commitChanges()
        else:
            self.layer.rollBack()
        self.attdlg.finished.disconnect(self.commitEdit)


    # レイヤウィンドウでレイヤを選択したときに呼ばれる
    def changeLayer(self, layer):
        if (layer == None) or (type(layer) is not qgis.core.QgsVectorLayer):
            return

        self.layer.removeSelection()
        self.layer = layer
        self.mouseEventSample.setLayer(self.layer)


class FeatureSelectionTool(qgis.gui.QgsMapToolIdentifyFeature):
    def __init__(self, canvas):
        self.canvas = canvas
        qgis.gui.QgsMapToolIdentifyFeature.__init__(self, self.canvas)

    def keyPressEvent( self, e ):
        pass
