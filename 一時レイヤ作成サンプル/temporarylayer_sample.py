# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TemporaryLayerSample
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

from PyQt5.Qt import pyqtSignal

class TemporaryLayerSample(QgsMapTool):

    def setGeometry(self, geom):
        qf = QgsFields()
        for field in self.tmplayer.fields():
            qf.append(QgsField(str(field.name()), typeName=field.typeName()))
        record = QgsFeature(qf) 
        # 地物をセットする
        record.setGeometry(geom) 
        # 属性をセットする
        record.setAttributes([])
        # 作成したレコードをレイヤに追加
        self.tmplayer.dataProvider().addFeatures([record])
        self.tmplayer.updateExtents()
        self.canvas.refreshAllLayers()


    def start(self):
        # 一時レイヤ作成
        typestr  = 'Polygon?'
        fieldstr = '&field=〇〇:string&field=□□:double&field=××:date'
        crsstr   = '&crs=' + str(QgsProject.instance().crs().authid())
        layername= '一時レイヤ'
        self.tmplayer = QgsVectorLayer(typestr + crsstr + fieldstr, layername, "memory")
        QgsProject.instance().addMapLayer(self.tmplayer)

        # ラバーバンドのための設定
        self.objtype     = QgsWkbTypes.PolygonGeometry # QgsWkbTypes.PointGeometry, QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry

        maptool = RubberBandClass(self.iface, self.canvas, self.objtype)
        maptool.getObject.connect(self.setGeometry)

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = '一時レイヤ作成サンプル' # プラグイン名
        self.menu_pos    = 'サンプル'             # プラグインの登録場所
        self.toolbar     = True                   # Trueならツールバーにアイコンを表示する
        self.checkable   = True                   # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, TemporaryLayerSample):
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


class RubberBandClass(QgsMapTool):
    getObject = pyqtSignal(QgsGeometry)

    def __init__(self, iface, canvas, type):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.iface = iface
        self.type = type

        self.myRubberBand = None


    def canvasMoveEvent(self, event):
        if self.myRubberBand == None: # 一度も左ボタンをクリックしてない時にこのメソッドが呼ばれた場合
            return

        # 地物の描画中に、マウスカーソルを追って形状が変わるように
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        self.myRubberBand.movePoint(point)


    def canvasPressEvent(self, event):
        currentPos = self.toMapCoordinates(event.pos())

        # 地物の最初の一点目
        if event.button() == Qt.LeftButton and self.myRubberBand == None:
            if self.type == QgsWkbTypes.PointGeometry:
                self.getObject.emit(QgsGeometry.fromPointXY(currentPos))
                return
            else:
                self.myRubberBand = QgsRubberBand( self.canvas, self.type )
                self.myRubberBand.setColor( QColor(255, 0, 0, 128) )
                self.myRubberBand.addPoint( QgsPointXY(currentPos) )

        # 地物の二点目以降
        if event.button() == Qt.LeftButton and self.myRubberBand.numberOfVertices() > 0:
            self.myRubberBand.addPoint( QgsPointXY(currentPos) )

        # オブジェクト確定
        if event.button() == Qt.RightButton:
            if self.myRubberBand == None:
                return

            self.getObject.emit(self.myRubberBand.asGeometry()) # ラバーバンドのオブジェクト取り出し


            self.canvas.scene().removeItem(self.myRubberBand) # ラバーバンドで描いた図形はもう必要ないので消す
            self.myRubberBand = None


    def deactivate(self):
        try: # 右クリックしてmyRubberBandを解放していた場合は例外発生するので。
            self.myRubberBand.reset(True)
        except:
            pass