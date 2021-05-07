# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .mouseeventlog_sample import MouseEventLogSample
    return MouseEventLogSample(iface)
