# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .multiobjectedit_sample import MultiObjectEditSample
    return MultiObjectEditSample(iface)
