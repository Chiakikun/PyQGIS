# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RuleBaseSample
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
from .rulebasesample import RuleBaseSample

execSampleの以下の部分を書き換える
        else:
            pass
から
        else:
            self.rulebase = RuleBaseSample(self.iface, self.canvas, self.iface.activeLayer())
            style_rules = (
                ('Target', '$id = 0', '#ff0000'), # $idが0なら赤
                ('Other',  'ELSE',    '#ffffff') # それ以外は白
            )
            self.rulebase.initColors(style_rules)
"""
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsSymbol, QgsRuleBasedRenderer


class RuleBaseSample:

    def __init__(self, iface, canvas, layer):

        self.canvas = canvas
        self.iface = iface
        self.layer = layer

        symbol = QgsSymbol.defaultSymbol(self.layer.geometryType())
        self.renderer = QgsRuleBasedRenderer(symbol)

        self.root_rule = self.renderer.rootRule()


    def initColors(self, rules):

        for label, expression, color_name in rules:
            rule = self.root_rule.children()[0].clone() # ラベル、フィルタ、色以外はデフォルト
 
            rule.setLabel(label)
            rule.setFilterExpression(expression)
            rule.symbol().setColor(QColor(color_name))

            self.root_rule.appendChild(rule)
        self.root_rule.removeChildAt(0)

        self.layer.setRenderer(self.renderer)
        self.layer.triggerRepaint()


    def setExpression(self, expression, index):
        self.root_rule.children()[index].setFilterExpression(expression)
        self.layer.setRenderer(self.renderer)
        self.layer.triggerRepaint()


    def __del__(self):
        pass