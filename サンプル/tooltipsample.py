# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToolTipSample
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
from .tooltipsample import ToolTipSample

③startの「maptool = self」を以下に書き換える
"""
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QToolTip
import qgis
from qgis.core import *
from qgis.gui  import *


class ToolTipSample(QgsMapTool):
    def __init__(self, canvas, ms): # msはミリ秒
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas

        self.ms = ms
        # canvasMoveEventで設定した秒数（msで設定）経過したら呼ばれるメソッドを設定
        self.timerMapTips = QTimer( canvas )
        self.timerMapTips.timeout.connect( self.showMapTip )


    def canvasMoveEvent(self, event):
        QToolTip.hideText()
        self.timerMapTips.start(self.ms)


    def showMapTip( self ):
        self.timerMapTips.stop()

        # 表示する値を設定する。この辺は適当に変えて。
        mappos = self.toMapCoordinates(self.canvas.mouseLastXY())
        value = mappos

        if value == None:
            return
        text = str(value)
        QToolTip.showText( self.canvas.mapToGlobal( self.canvas.mouseLastXY() ), text, self.canvas )


    def deactivate(self):
        self.timerMapTips.timeout.disconnect( self.showMapTip )
