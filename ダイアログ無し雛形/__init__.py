# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .nodialog_skelton import NodialogSkelton
    return NodialogSkelton(iface)
