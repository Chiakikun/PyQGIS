﻿# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RubberBandSampleDialog
                                 A QGIS plugin
 RubberBandのSampleです
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-23
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
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from qgis.PyQt.QtGui import QColor
import os
import qgis.core
from datetime import datetime

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'maptoolemitpoint_sample_dialog_base.ui'))


class RubberBandSampleDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(RubberBandSampleDialog, self).__init__(parent)
        self.setupUi(self)

        self.canvas = iface.mapCanvas()

        # 仮想レイヤ作成
        self.vlyr = qgis.core.QgsVectorLayer("Polygon?&crs=epsg:4326&field=name:string&field=size:double", "サンプルレイヤ", "memory")
        # キャンバスウィンドウ上でのマウスイベントの設定
        self.mouseEventSample = qgis.gui.QgsMapToolEmitPoint(self.canvas)


    def unsetTool(self):
        self.pushButton_Exec.setChecked(False)


    def closeEvent(self, e):
        try:
            self.pushButton_Exec.setChecked(False)
        except:
            pass
 

    def pushClose(self):
        self.close()


    def pushExec(self, checked):
        if checked == True:
            self.mouseEventSample.canvasClicked.connect(self.mouseClick)
            self.mouseEventSample.canvasMoveEvent = self.canvasMoveEvent        
            self.canvas.setMapTool(self.mouseEventSample)

            self.canvas.mapToolSet.connect(self.unsetTool)
            self.pushButton_Exec.setText('実行中')

            self.myRubberBand = None
        else:
            try: # 右クリックしてmyRubberBandを解放していた場合は例外発生するので。
                self.myRubberBand.reset(True)
            except:
                pass

            self.pushButton_Exec.setText('実行')

            self.canvas.mapToolSet.disconnect(self.unsetTool)
            self.canvas.unsetMapTool(self.mouseEventSample)
            self.mouseEventSample.canvasClicked.disconnect(self.mouseClick)


    def canvasMoveEvent(self, event):
        if self.myRubberBand == None: # 一度も左ボタンをクリックしてない時にこのメソッドが呼ばれた場合
            return

        # 地物の描画中に、マウスカーソルを追って形状が変わるように
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        self.myRubberBand.movePoint(point)


    def mouseClick(self, currentPos, clickedButton ):
        # 地物の最初の一点目
        if clickedButton == QtCore.Qt.LeftButton and self.myRubberBand == None:
            self.myRubberBand = qgis.gui.QgsRubberBand( self.canvas, qgis.core.QgsWkbTypes.PolygonGeometry )
            self.myRubberBand.setColor( QColor(78, 97, 114, 190) )
            self.myRubberBand.addPoint( qgis.core.QgsPointXY(currentPos) )

        # 地物の二点目以降
        if clickedButton == QtCore.Qt.LeftButton and self.myRubberBand.numberOfVertices() > 0:
            self.myRubberBand.addPoint( qgis.core.QgsPointXY(currentPos) )

        # __init__で作成した仮想レイヤのレコード作成
        if clickedButton == QtCore.Qt.RightButton:
            # フィールド設定
            qf = qgis.core.QgsFields()
            for field in self.vlyr.fields():
                qf.append(qgis.core.QgsField(str(field.name()), typeName=field.typeName()))
            record = qgis.core.QgsFeature(qf) 

            # ラバーバンドで作成した地物をセットする
            geomP = self.myRubberBand.asGeometry() 
            record.setGeometry(geomP) 

            # 属性をセットする
            record.setAttributes([str(datetime.now()), geomP.area()])

            # 作成したレコードをレイヤに追加
            self.vlyr.dataProvider().addFeatures([record])
            self.vlyr.updateExtents() # これが無いと『レイヤの領域にズーム』した時に、レイヤの最初のオブジェクト部分しかズームされない

            # キャンバスにオブジェクトを表示する      
            qgis.core.QgsProject.instance().addMapLayers([self.vlyr])
            #self.canvas.setExtent(geomP.boundingBox()) #パンしたい場合は#外して
            self.canvas.refreshAllLayers()

            self.canvas.scene().removeItem(self.myRubberBand) # ラバーバンドで描いた図形はもう必要ないので消す
            self.myRubberBand = None

