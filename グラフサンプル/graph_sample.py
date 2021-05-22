# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GraphSample
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
from qgis.PyQt.QtWidgets import QAction,QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import qgis
from qgis.core import *
from qgis.gui  import *

import matplotlib.pyplot as plt
import numpy as np
from .rubberband import RubberBand
from .getrasterpixelvalue import GetRasterPixelValue
import datetime
import math

class GraphSample(QgsMapTool):

    # lineLLを垂直に横断する点列を作成する
    def addOdansen(self, lineLL, key):

        def angle(a, b):
            return math.atan2(b.y() - a.y(), b.x() - a.x())

        # startからrad方向にn進んだ位置を返す
        def destination(start, rad, n):
            return QgsPointXY(n * math.cos(rad) + start.x(), n * math.sin(rad) + start.y())

        def transformCRS(obj, src, dst):
            newobj = QgsGeometry(obj)
            srcCrs = QgsCoordinateReferenceSystem(src)
            dstCrs = QgsCoordinateReferenceSystem(dst)
            tr = QgsCoordinateTransform(srcCrs, dstCrs, QgsProject.instance())
            newobj.transform(tr)
            return newobj

        # startpnt、endpntが成す線分の、startpntからlength分進んだ位置を中心に、線分を横断する線を作成する。
        # cntは番号付けのために使っている。
        def odansen(startpnt, endpnt, length, cnt):
            center = destination(startpnt, angle(startpnt, endpnt), length)
            rad = angle(startpnt, endpnt) + (-90 * math.pi / 180)

            for i in range(-self._odanlinelength, self._odanlinelength + self._odanpointspan, self._odanpointspan):
                xypnt = QgsGeometry().fromPointXY(destination(center, rad, i))
                llpnt = transformCRS(xypnt, self._xycrs, self._llcrs)

                elev = self.gr.getValueInterpolation(llpnt.asPoint())
                self.addFeature(self.hol, llpnt, [key, cnt, i, elev])

         
        lineXY = transformCRS(lineLL, self._llcrs, self._xycrs) # 描画したラインは緯度経度の座標なので、平面直角座標に変換する
        judanLen = lineXY.length()
        pnts = [pnt for pnt in lineXY.asPolyline()]

        # 縦断線の始点を横断する線
        odansen(pnts[0], pnts[1], 0, 0)

        cnt = 1
        nextpos = self._odanlinespan * cnt

        while judanLen > nextpos:

            for i in range(1, len(pnts)):

                nodelength = pnts[i-1].distance(pnts[i])
                # この線分上に横断線引ける？
                # 引けない
                if (nextpos - nodelength) > 0:
                    nextpos -= nodelength
                # 引ける
                else:
                    odansen(pnts[i - 1], pnts[i], nextpos, cnt)

                    cnt += 1
                    nextpos = self._odanlinespan * cnt
                    break

        # 縦断線の終点を横断する線
        odansen(pnts[-2], pnts[-1], pnts[-1].distance(pnts[-2]), cnt)


    def setFeature(self, geom):
        def getNumber(feature):
            return feature['pointcount']

        key = datetime.datetime.now().strftime('%Y%m%d%H%M%S') # 縦断線と横断線を紐付けるキー
        self.addFeature(self.ver, geom, [key]) # 縦断線レイヤに、描画したラインを追加
        self.addOdansen(geom, key)             # 描画したラインを横断する点列を横断戦レイヤに追加
        
        # グラフ作成
        features = list(self.hol.getFeatures(QgsFeatureRequest().setFilterExpression('"key"='+'\'' + key + '\'')))
        linenumbers = sorted(set([f['linecount'] for f in features]))
        for linenumber in linenumbers:
            linenode = sorted([f for f in features if f['linecount'] == linenumber], key=getNumber) # 'pointcount'の値順に並び変える

            fig, ax = plt.subplots()
            y = np.array([l['elev'] for l in linenode])
            x = np.array([l['pointcount'] for l in linenode])
            ax.set_title(str(linenode[0]['key']) + '_' + str(linenumber))
            ax.plot(x, y, '-')
            plt.savefig(self._savedir + str(linenode[0]['key']) + '_' + str(linenumber) + '.png')


    # 一時レイヤ作成
    def createTemporaryLayer(self, layername, type, fieldsstr):
        epsg = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        layer = QgsVectorLayer(type + '?&crs='+epsg+fieldsstr, layername, 'memory')

        QgsProject.instance().addMapLayer(layer)
        return layer


    # レイヤにレコード追加
    def addFeature(self, layer, geometry, attrs):
        qf = QgsFields()
        for field in layer.fields():
            qf.append(QgsField(str(field.name()), typeName=field.typeName()))
        record = QgsFeature(qf) 

        # 地物をセットする
        record.setGeometry(geometry) 

        # 属性をセットする
        record.setAttributes(attrs)

        # 作成したレコードをレイヤに追加
        layer.dataProvider().addFeatures([record])
        layer.updateExtents() # これが無いと『レイヤの領域にズーム』した時に、レイヤの最初のオブジェクト部分しかズームされない

        self.canvas.refreshAllLayers()


    def start(self):
        # このプログラム使うときはこの辺を調整してください
        self._llcrs = 4326
        self._xycrs = 2451 # 千葉県のDEMでテストしたので9系になってます。
        self._savedir = 'c:\\users\\〇〇\\desktop\\pic\\' # 横断図の保存先
        self._odanlinespan   = 100 # 横断線の間隔
        self._odanlinelength = 200 # 横断線の片側の長さ
        self._odanpointspan  = 10  # 横断線上のサンプリング間隔

        self.gr = GetRasterPixelValue(self.iface.activeLayer())

        maptool = RubberBand(self.iface, self.canvas, QgsWkbTypes.LineGeometry)
        maptool.getObject.connect(self.setFeature)

        self.ver = self.createTemporaryLayer('縦断線', 'LineString', '&field=key:string')
        self.hol = self.createTemporaryLayer('横断線', 'Point',      '&field=key:string&field=linecount:integer&field=pointcount:integer&field=elev:double')

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def finish(self):
    
        self.ver = None
        self.hol = None
        self.gr = None

        self.canvas.mapToolSet.disconnect(self.unsetTool)


    def __init__(self, iface):
        self.plugin_name = 'グラフサンプル' # プラグイン名
        self.menu_pos    = 'サンプル'               # プラグインの登録場所(このサンプルの場合、メニューの「プラグイン/雛形/ダイアログ無し雛形」)
        self.toolbar     = True                 # Trueならツールバーにアイコンを表示する
        self.checkable   = True                 # Trueならプラグイン実行中はアイコンが凹んだままになる

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QgsMapTool.__init__(self, self.canvas)


    # このプラグイン実行中に他のアイコンが押された場合、アイコンを元の状態に戻す
    def unsetTool(self, tool):
        if not isinstance(tool, GraphSample):
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
