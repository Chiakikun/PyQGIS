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
使い方例（『https://github.com/Chiakikun/PyQGIS/blob/master/ダイアログ無し雛形/nodialog_skelton.py』に組み込む場合）

①プラグインのフォルダにこのファイルを置く

②インポート部分に以下を追加する
from .relationsample import RelationSample

④startを以下で置き換える
    def start(self):
        # 国土数値情報ダウンロードサービスからダウンロードできる行政区画と避難所を使う場合
        parent = QgsProject.instance().mapLayersByName('行政区画')[0]
        child =QgsProject.instance().mapLayersByName('避難所')[0]
        self.rel = RelationSample(self.iface, parent, 'N03_007', child, 'p20_001')


⑤finishを以下で置き換える
    def finish(self):
        self.rel = None

⑥プラグインを実行したら、親レイヤ（ここでは行政区画）の地物を一つ選択すると、子レイヤ（ここでは避難所）の属性テーブルが表示される
"""
from qgis.PyQt import QtWidgets
from qgis.PyQt.Qt import QSettings
import qgis
from qgis.core import *
from qgis.gui  import *

class RelationSample:

    def __init__(self, iface, parentLayer, parentField, childLayer, childField):

        self.iface = iface

        self.rel = QgsRelation()
        self.rel.setReferencingLayer(childLayer.id())
        self.rel.setReferencedLayer(parentLayer.id())
        self.rel.addFieldPair(childField, parentField)
        self.rel.setId('適当なID')
        self.rel.setName('適当な名前')
        QgsProject.instance().relationManager().addRelation(self.rel)

        self.parent = parentLayer
        self.parent.selectionChanged.connect(self.showChildren)


    def showChildren(self):
        parent = self.rel.referencedLayer()
        child = self.rel.referencingLayer()

        features = parent.selectedFeatures()
        if len(features) == 0:
            return

        child.removeSelection() # クリアしないと、属性テーブルに余計に表示されるから 
        for c in self.rel.getRelatedFeatures(features[0]):
            child.select(c.id())

        selectedlayer = self.iface.activeLayer() # 退避
        try:
            # このプログラム実行中は属性テーブルは選択中のフューチャーしか表示しない
            self.oldsetting = QSettings().value('/Qgis/attributeTableBehaviour')
            QSettings().setValue('/Qgis/attributeTableBehavior', 'ShowSelected')

            self.iface.setActiveLayer(child)
            self.iface.mainWindow().findChild(QtWidgets.QAction, 'mActionOpenTable' ).trigger()
        finally:
            self.iface.setActiveLayer(selectedlayer) # 戻す
            QSettings().setValue('/Qgis/attributeTableBehavior', self.oldsetting)


    def __del__(self):
        QgsProject.instance().relationManager().removeRelation(self.rel)
        self.parent.selectionChanged.disconnect(self.showChildren)
