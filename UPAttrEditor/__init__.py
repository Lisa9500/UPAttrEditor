# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UPAttrEditor
                                 A QGIS plugin
 Attribute Editor for 3D City Model
                             -------------------
        begin                : 2016-07-11
        copyright            : (C) 2016 by Toshio Yamazaki / UPCS
        email                : lisa9500jp@gmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load UPAttrEditor class from file UPAttrEditor.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .up_attr_editor import UPAttrEditor
    return UPAttrEditor(iface)
