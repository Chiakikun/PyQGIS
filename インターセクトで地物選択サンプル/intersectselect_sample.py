# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IntersectSelectSample
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


class IntersectSelectSample(QgsMapTool):

    def intersectSelect1(self, selectLayer, intersectLayer):
        selectLayer.removeSelection()

        sel = []
        for feat in intersectLayer.selectedFeatures():
            geom = feat.geometry()

            cands = selectLayer.getFeatures(QgsFeatureRequest().setFilterRect(geom.boundingBox()))
            for sf in cands:
                if geom.intersects(sf.geometry()):
                    sel.append(sf.id())
            selectLayer.select(sel)


    def intersectSelect2(self, selectLayer, intersectLayer):
        qgis.processing.run("native:selectbylocation",\
            {\
            'INPUT':selectLayer,\
            'PREDICATE':[0],\
            'INTERSECT':QgsProcessingFeatureSourceDefinition(intersectLayer.name(), selectedFeaturesOnly=True),\
            'METHOD':0\
            })


    def start(self):
        selectLayer = QgsProject.instance().mapLayersByName('〇〇')[0]
        intersectLayer = QgsProject.instance().mapLayersByName('〇〇')[0]

        self.intersectSelect2(selectLayer, intersectLayer)


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'インターセクトで地物選択' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛形/ダイアログ無し雛形」)
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = False                # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, IntersectSelectSample):
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
