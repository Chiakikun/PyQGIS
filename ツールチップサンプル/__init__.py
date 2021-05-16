# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .tooltip_sample import ToolTipSample
    return ToolTipSample(iface)
