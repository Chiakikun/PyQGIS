# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RubberBandSample
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

③setConnectの「maptool = self」を以下に書き換える
        maptool = RubberBandSample(self.iface, self.canvas, QgsWkbTypes.LineGeometry)  # ラインの場合

"""
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

import qgis
from qgis.core import *
from qgis.gui  import *

class RubberBandSample(QgsMapTool):

    def __init__(self, iface, canvas, type): # type = QgsWkbTypes.PointGeometry, QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry
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

            # geom = self.myRubberBand.asGeometry() # ラバーバンドのオブジェクト取り出し

            self.canvas.scene().removeItem(self.myRubberBand) # ラバーバンドで描いた図形はもう必要ないので消す
            self.myRubberBand = None


    def deactivate(self):
        try: # 右クリックしてmyRubberBandを解放していた場合は例外発生するので。
            self.myRubberBand.reset(True)
        except:
            pass
