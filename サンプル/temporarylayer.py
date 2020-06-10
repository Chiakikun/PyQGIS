# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TemporaryLayer
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

①「https://raw.githubusercontent.com/Chiakikun/PyQGIS/master/%E3%82%B5%E3%83%B3%E3%83%97%E3%83%AB/rubberbandSample.py」をダウンロードする

②プラグインのフォルダにこのファイルと①を置く

③インポートに以下を追加する
from .rubberbandSample import RubberBandSample
from .temporarylayer import TemporaryLayer

③startを以下に書き換える
    def start(self):
        maptool = RubberBandSample(self.iface, self.canvas, QgsWkbTypes.PolygonGeometry)  # ポリゴンの場合
        maptool.getObject.connect(self.setFeature)

        fields = [
            'id:integer',
            'name:string'
        ]
        self.tmp = TemporaryLayer(self.iface, self.canvas, '一時レイヤ', 'Polygon', fields)

        self.canvas.setMapTool(maptool)
        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合

④finishを以下に書き換える
    def finish(self):
        self.tmp = None
        self.canvas.mapToolSet.disconnect(self.unsetTool)

⑤次のメソッドを追加する
    def setFeature(self, geom):
        self.tmp.addFeature(geom, []) # 今回は属性には何も入れていません

"""
import qgis
from qgis.core import *
from qgis.gui  import *

class TemporaryLayer:
    def __init__(self, iface, canvas, layername, type, fields): # type = Point or LineString, Polygon

        self.canvas = canvas
        self.iface = iface

        fieldsstr = ''
        for f in fields:
            fieldsstr += '&field=' + f

        epsg = iface.mapCanvas().mapSettings().destinationCrs().authid()
        self.layer = QgsVectorLayer(type + '?&crs='+epsg+fieldsstr, layername, 'memory')

        QgsProject.instance().addMapLayer(self.layer)

    def addFeature(self, geometry, attrs):

            qf = QgsFields()
            for field in self.layer.fields():
                qf.append(QgsField(str(field.name()), typeName=field.typeName()))
            record = QgsFeature(qf) 

            # 地物をセットする
            record.setGeometry(geometry) 

            # 属性をセットする
            record.setAttributes(attrs)

            # 作成したレコードをレイヤに追加
            self.layer.dataProvider().addFeatures([record])
            self.layer.updateExtents() # これが無いと『レイヤの領域にズーム』した時に、レイヤの最初のオブジェクト部分しかズームされない

            self.canvas.refreshAllLayers()


    def __del__(self):
        self.canvas.refreshAllLayers()
        QgsProject.instance().removeMapLayer(self.layer.id())
