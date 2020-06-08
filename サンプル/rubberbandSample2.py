# -*- coding: utf-8 -*-
"""
RubberBandSampleのマルチオブジェクト対応版です
/***************************************************************************
 RubberBandSample2
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
使い方例（『https://github.com/Chiakikun/PyQGIS/blob/master/ダイアログ無し雛形/nodialog_skelton.py』に組み込む場合）

①プラグインのフォルダにこのファイルを置く

②インポートに以下を追加する
from .rubberbandSample import RubberBandSample

③startの「maptool = self」を以下に書き換える
        maptool = RubberBandSample(self.iface, self.canvas, QgsWkbTypes.LineGeometry)  # ラインの場合
        maptool.getObject.connect(self.printGeometry)

④次のメソッドを追加する
    def printGeometry(self, geom):
        print(geom)
"""
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from PyQt5.Qt import pyqtSignal
import qgis
from qgis.core import *
from qgis.gui  import *

class RubberBandSample(QgsMapTool):
    getObject = pyqtSignal(QgsGeometry)

    def __init__(self, iface, canvas, type): # type = QgsWkbTypes.PointGeometry, QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.iface = iface
        self.type = type

        self.myRubberBand = None
        self.myRubberBands = [] # 使用済みのラバーバンドを格納しておく場所 # NEW


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

            # ラバーバンドで作成した地物をセットする
            self.myRubberBand.removeLastPoint() # 右クリックした時のカーソル位置のポイントは含めない
            self.myRubberBands.append(self.myRubberBand)
            if self.type == QgsWkbTypes.PolygonGeometry:
                geom = self.RubberBandsToPolygon()
            elif self.type == QgsWkbTypes.LineGeometry:
                geom = self.RubberBandsToLine()
            elif self.type == QgsWkbTypes.PointGeometry:
                geom = self.RubberBandsToPoint()
            self.getObject.emit(geom) # ラバーバンドのオブジェクト取り出し


            self.canvas.scene().removeItem(self.myRubberBand) # ラバーバンドで描いた図形はもう必要ないので消す
            self.myRubberBand = None
            self.myRubberBands = []           # new
            self.canvas.refreshAllLayers()    # new


    # NEW
    def canvasDoubleClickEvent(self, event):
        if self.myRubberBand == None:
            return

        if self.type == QgsWkbTypes.PointGeometry:
            return

        if self.myRubberBand.numberOfVertices() == 2:
            self.myRubberBand = None
            return

        self.myRubberBand.removeLastPoint()

        self.myRubberBands.append(self.myRubberBand)
        self.myRubberBand = None 


    def deactivate(self):
        try: # 右クリックしてmyRubberBandを解放していた場合は例外発生するので。
            for i in range(0, len(self.myRubberBands)):                    # New
                self.canvas.scene().removeItem(self.myRubberBands[i])      # New
            self.myRubberBand.reset(True)
        except:
            pass


    def RubberBandsToPolygon(self):
        mpol = []
        for i in range(0, len(self.myRubberBands)):
            if self.myRubberBands[i] == None: continue
            mpol.append([[]])
            for pnts in self.myRubberBands[i].asGeometry().asPolygon(): 
                for pnt in pnts:
                    mpol[len(mpol)-1][0].append(pnt)
            self.canvas.scene().removeItem(self.myRubberBands[i])

        if len(self.myRubberBands) == 1:
            return qgis.core.QgsGeometry().fromPolygonXY(mpol[0]) 
        else:
            return qgis.core.QgsGeometry().fromMultiPolygonXY(mpol) 


    def RubberBandsToLine(self):
        mline = []
        for i in range(0, len(self.myRubberBands)):
            if self.myRubberBands[i] == None: continue
            mline.append([])
            for pnts in self.myRubberBands[i].asGeometry().asPolyline(): 
                mline[len(mline)-1].append(pnts)
            self.canvas.scene().removeItem(self.myRubberBands[i])

        if len(self.myRubberBands) == 1:
            return qgis.core.QgsGeometry().fromPolylineXY(mline[0]) 
        else:
            return qgis.core.QgsGeometry().fromMultiPolylineXY(mline) 


    def RubberBandsToPoint(self):
        mpnt = []
        for i in range(0, len(self.myRubberBands)):
            if self.myRubberBands[i] == None: continue
            for pnt in self.myRubberBands[i].asGeometry().asMultiPoint():
                mpnt.append(pnt)
            self.canvas.scene().removeItem(self.myRubberBands[i])
        if len(mpnt) == 1:
            return qgis.core.QgsGeometry().fromPointXY(mpnt[0]) 
        else:
            return qgis.core.QgsGeometry().fromMultiPointXY(mpnt) 
