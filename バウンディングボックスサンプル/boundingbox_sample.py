# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BoundingBox Sample
        copyright            : (C) 2021 by Chiakikun
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


class BoundingBoxSample(QgsMapTool):

    def start(self):

        srclayer = self.iface.activeLayer()
        if (srclayer == None) or (type(srclayer) is not QgsVectorLayer):
            QMessageBox.about(None, '警告', 'ベクタレイヤを選択してから実行してください')
            self.action.setChecked(False)
            return
        dstlayer = QgsVectorLayer("Polygon?crs=epsg:4326&field=pref:string", "サンプルレイヤ", "memory")

        for f in srclayer.getFeatures():
            mpol = f.geometry().asMultiPolygon()

            for i in range(0, len(mpol)):
                bnd = QgsGeometry.fromRect(QgsGeometry().fromPolygonXY(mpol[i]).boundingBox())

                for b in bnd.asPolygon():
                    # 属性
                    qf = QgsFields()
                    for field in dstlayer.fields():
                        qf.append(QgsField(str(field.name()), typeName=field.typeName()))
                    record = QgsFeature(qf)
                    record[0] = f[1]
                    # オブジェクト
                    record.setGeometry(QgsGeometry.fromPolygonXY([b]))
                    # レイヤに追加
                    dstlayer.dataProvider().addFeatures([record])
                    dstlayer.updateExtents()

        # キャンバスにオブジェクトを表示する      
        QgsProject.instance().addMapLayers([dstlayer])
        self.canvas.refreshAllLayers()


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'バウンディングボックス作成サンプル' # プラグイン名
        self.menu_pos    = 'サンプル'           # プラグインの登録場所
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = False                # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, BoundingBoxSample):
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
