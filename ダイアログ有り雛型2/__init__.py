# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Tool Form sample
        begin                : 2022-02-20
        copyright            : (C) 2022 by Chiakikun
        email                : chiakikungm@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    from .tool_form import ToolForm
    return ToolForm(iface)
