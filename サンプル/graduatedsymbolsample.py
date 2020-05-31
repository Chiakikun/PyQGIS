# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GraduatedSymbolSample
        git sha              : $Format:%H$
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
from .graduatedsymbolsample import GraduatedSymbolSample

__init__のcheckableをFalseにする
self.checkable = False

execSampleの以下の部分を書き換える
        else:
            pass
から
        else:
            self.gr = GraduatedSymbolSample(self.iface, self.canvas, 'elev') # elevは色設定に使うフィールド名に書き換えて
            style_rules = (
                (0,     30, '#ffffff'),
                (30.1,  60, '#ffcccc'),
                (60.1, 90, '#ff9999'),
                (90.1, 120, '#ff6666'),
                (120.1, 150, '#ff3333'),
                (150.1, 180, '#ff0000')
            )
            self.gr.setColor(self.iface.activeLayer(), style_rules)
に書き換え

"""
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsSymbol, QgsRendererRange, QgsGraduatedSymbolRenderer


class GraduatedSymbolSample:

    def __init__(self, iface, canvas, fieldname):
        self.canvas = canvas
        self.iface = iface
        self.field = fieldname


    def setColor(self, layer, rules): # rule = min, max, color
        if layer.geometryType() == 4: return

        rangelist = []
        for minv, maxv, color_name in rules:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.symbolLayer(0).setStrokeColor(QColor('transparent'))
            symbol.setColor(QColor(color_name))        
            rangelist.append( QgsRendererRange(minv, maxv, symbol, str(minv) +' - '+ str(maxv)) )

        self.renderer = QgsGraduatedSymbolRenderer(self.field, rangelist)
        self.renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(self.renderer)
        layer.triggerRepaint()


    def __del__(self):
        pass
