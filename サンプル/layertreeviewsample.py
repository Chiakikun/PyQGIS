# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerTreeViewSample
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

プラグインのフォルダにこのファイルを置く

インポート
from .layertreeviewsample import LayerTreeViewSample

startを次に変更する
    def start(self):
        self.lt = LayerTreeViewSample(self.iface)

finishを次に変更する
    def finish(self):
        self.lt = None

"""
import qgis
from qgis.core import *
from qgis.gui  import *
from PyQt5.Qt import QObject, pyqtSignal

class LayerTreeViewSample(QObject): # signal-slot使いたいので
    cleared = pyqtSignal()

    def changeLayer(self, layer):

        if (layer == None): # レイヤウィンドウに何も無い状態
            self.currentlayer = None
            self.cleared.emit()
            return

        if self.currentlayer != None:
            print(self.currentlayer.name() + 'が非アクティブになりました。')

        print(layer.name()+'がアクティブになりました。')
        self.currentlayer = layer


    def __init__(self, iface):
        super(LayerTreeViewSample, self).__init__()

        self.iface = iface

        self.currentlayer = self.iface.layerTreeView().currentLayer()
        self.iface.layerTreeView().currentLayerChanged.connect(self.changeLayer)


    def __del__(self):
        self.iface.layerTreeView().currentLayerChanged.disconnect(self.changeLayer)
