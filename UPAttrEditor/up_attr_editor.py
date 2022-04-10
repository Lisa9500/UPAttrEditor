# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UPAttrEditor
                                 A QGIS plugin
 Attribute Editor for 3D City Model
                              -------------------
        begin                : 2016-07-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Toshio Yamazaki / UPCS
        email                : lisa9500jp@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# IMPORT MODULES
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from up_attr_editor_dialog import UPAttrEditorDialog
import os.path
import sys

class UPAttrEditor:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'UPAttrEditor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = UPAttrEditorDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&UP Attr Editor')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'UPAttrEditor')
        self.toolbar.setObjectName(u'UPAttrEditor')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UPAttrEditor', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/UPAttrEditor/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'UP Attr Editor'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&UP Attr Editor'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        # PREPARE COMBO BOX
        self.dlg.comboBox.clear()

        layers = self.iface.legendInterface().layers()
        # self.dlg.textBrowser.setText(str(layers))
        # layersにはレイヤ名がリスト型で格納されている

        # SET LAYER NAME INTO COMBO BOX
        layer_list = []
        # layer_listはunicodeのオブジェクトであり，属性情報を持っていない
        newLayers = []
        for layer in layers:
            # if layer.type() == 0 or layer.type() == 1:
            if layer.type() == 0:
            # レイヤタイプの確認　0:vector or 1:raster
                layer_list.append(layer.name())
                newLayers.append(layer)
        self.dlg.comboBox.addItems(layer_list)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            index = self.dlg.comboBox.currentIndex()
            # currentIndex()でcomboBoxの中のレイヤーを選択できる
            # self.dlg.textBrowser.setText(str(index))

            aLayer = layers[index]
            fields = aLayer.pendingFields()
            # self.dlg.textBrowser.setText(str(fields))
            # <qgis._core.QgsFields object at 0x17257B20>
            field_names = [field.name() for field in fields]
            # self.dlg.textBrowser.setText(str(field_names))
            # field_namesはリスト型で，ユニコード文字でフィールド名が格納されている

            provider = aLayer.dataProvider()

            # MAKE ATTRIBUTE DATA TABLE
            data = []
            for i in range(len(fields)):
                # fieldsの要素数をlen()関数で取得している
                data += [[]]
                # リスト型のデータの入れ物を作っている
            for feat in provider.getFeatures():
                # self.dlg.textBrowser.setText(str(feat))
                attrs = feat.attributes()
                # self.dlg.textBrowser.setText(str(attrs))
                # attrsは各地物(feature)の属性データがリスト型で格納されている
                for i in range(len(attrs)):
                    # self.dlg.textBrowser.setText(str(len(attrs)))
                    # len(attrs)は属性項目の数を格納している
                    data[i] += [attrs[i]]

            # ATTRIBUTE DATA EDITING
            aLayer.startEditing()

            # 1_name Field Clone
            pr_1 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_2))
            pr_1.addAttributes([QgsField("1_name", QVariant.String)])
            aLayer.updateFields()

            movedData = data[9]

            for feat_1 in aLayer.getFeatures():
                attr_1Name = '1_name'
                pr_1.changeAttributeValues({feat_1.id() : {pr_1.fieldNameMap()[attr_1Name] : movedData[feat_1.id()]}})

            # 2_youto Field Adding
            pr_2 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_2))
            pr_2.addAttributes([QgsField("2_youto", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_2))

            for feat_2 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_2))

                youtoIndex = self.dlg.youtoBox.currentIndex()

                attr_2Name = '2_youto'
                if youtoIndex == 0:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 1}})
                elif youtoIndex == 1:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 2}})
                elif youtoIndex == 2:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 3}})
                elif youtoIndex == 3:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 4}})
                elif youtoIndex == 4:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 5}})
                elif youtoIndex == 5:
                    pr_2.changeAttributeValues({feat_2.id() : {pr_2.fieldNameMap()[attr_2Name] : 6}})

            # 3_story Field Adding
            pr_3 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_3))
            pr_3.addAttributes([QgsField("3_story", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_3))

            compData = data[8]

            for feat_3 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_3))

                attr_3Name = '3_story'
                # self.dlg.textBrowser.setText(attrs[9])
                if compData[feat_3.id()] == u"普通建物":
                    pr_3.changeAttributeValues({feat_3.id() : {pr_3.fieldNameMap()[attr_3Name] : 2}})
                elif compData[feat_3.id()] == u"普通無壁舎":
                    pr_3.changeAttributeValues({feat_3.id() : {pr_3.fieldNameMap()[attr_3Name] : 1}})
                elif compData[feat_3.id()] == u"堅ろう建物":
                    pr_3.changeAttributeValues({feat_3.id() : {pr_3.fieldNameMap()[attr_3Name] : 4}})
                elif compData[feat_3.id()] == u"堅ろう無壁舎":
                    pr_3.changeAttributeValues({feat_3.id() : {pr_3.fieldNameMap()[attr_3Name] : 1}})

            # 地下階数の追加
            # 4_basement Field Adding
            pr_4 = aLayer.dataProvider()
            pr_4.addAttributes([QgsField("4_basement", QVariant.Int)])
            aLayer.updateFields()

            for feat_4 in aLayer.getFeatures():
                attr_4Name = '4_basement'
                pr_4.changeAttributeValues({feat_4.id() : {pr_4.fieldNameMap()[attr_4Name] : 0}})
                # 地下階数は0階をデフォルトとする

            # 5_yanetype Field Adding
            pr_5 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_5))
            pr_5.addAttributes([QgsField("5_yanetype", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_5))

            for feat_5 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_5))

                yanetypeIndex = self.dlg.yanetypeBox.currentIndex()

                attr_5Name = '5_yanetype'
                if yanetypeIndex == 0:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 0}})
                elif yanetypeIndex == 1:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 1}})
                elif yanetypeIndex == 2:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 2}})
                elif yanetypeIndex == 3:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 3}})
                elif yanetypeIndex == 4:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 4}})
                elif yanetypeIndex == 5:
                    pr_5.changeAttributeValues({feat_5.id() : {pr_5.fieldNameMap()[attr_5Name] : 8}})

            # 6_incline Field Adding
            pr_6 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_6))
            pr_6.addAttributes([QgsField("6_incline", QVariant.Double)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_6))

            for feat_6 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat65))

                inclineIndex = self.dlg.inclineBox.currentIndex()

                attr_6Name = '6_incline'
                if inclineIndex == 0:
                    pr_6.changeAttributeValues({feat_6.id() : {pr_6.fieldNameMap()[attr_6Name] : 0.3}})
                elif inclineIndex == 1:
                    pr_6.changeAttributeValues({feat_6.id() : {pr_6.fieldNameMap()[attr_6Name] : 0.4}})
                elif inclineIndex == 2:
                    pr_6.changeAttributeValues({feat_6.id() : {pr_6.fieldNameMap()[attr_6Name] : 0.5}})
                elif inclineIndex == 3:
                    pr_6.changeAttributeValues({feat_6.id() : {pr_6.fieldNameMap()[attr_6Name] : 0.6}})

            # 7_hiratuma Field Adding
            pr_7 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_7))
            pr_7.addAttributes([QgsField("7_hiratuma", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_7))

            for feat_7 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_7))

                hiratumaIndex = self.dlg.hiratumaBox.currentIndex()

                attr_7Name = '7_hiratuma'
                if hiratumaIndex == 0:
                    pr_7.changeAttributeValues({feat_7.id() : {pr_7.fieldNameMap()[attr_7Name] : 1}})
                elif hiratumaIndex == 1:
                    pr_7.changeAttributeValues({feat_7.id() : {pr_7.fieldNameMap()[attr_7Name] : 2}})

            # 8_yanemuki Field Adding
            pr_8 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_8))
            pr_8.addAttributes([QgsField("8_yanemuki", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_8))

            for feat_8 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_8))

                yanemukiIndex = self.dlg.yanemukiBox.currentIndex()

                attr_8Name = '8_yanemuki'
                if yanemukiIndex == 0:
                    pr_8.changeAttributeValues({feat_8.id() : {pr_8.fieldNameMap()[attr_8Name] : 1}})
                elif yanemukiIndex == 1:
                    pr_8.changeAttributeValues({feat_8.id() : {pr_8.fieldNameMap()[attr_8Name] : 2}})
                elif yanemukiIndex == 2:
                    pr_8.changeAttributeValues({feat_8.id() : {pr_8.fieldNameMap()[attr_8Name] : 3}})
                elif yanemukiIndex == 3:
                    pr_8.changeAttributeValues({feat_8.id() : {pr_8.fieldNameMap()[attr_8Name] : 4}})

            # 9_hisashi Field Adding
            pr_9 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_9))
            pr_9.addAttributes([QgsField("9_hisashi", QVariant.Double)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_9))

            for feat_9 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_9))

                hisashiIndex = self.dlg.hisashiBox.currentIndex()

                attr_9Name = '9_hisashi'
                if hisashiIndex == 0:
                    pr_9.changeAttributeValues({feat_9.id() : {pr_9.fieldNameMap()[attr_9Name] : 0.3}})
                elif hisashiIndex == 1:
                    pr_9.changeAttributeValues({feat_9.id() : {pr_9.fieldNameMap()[attr_9Name] : 0.45}})
                elif hisashiIndex == 2:
                    pr_9.changeAttributeValues({feat_9.id() : {pr_9.fieldNameMap()[attr_9Name] : 0.6}})
                elif hisashiIndex == 3:
                    pr_9.changeAttributeValues({feat_9.id() : {pr_9.fieldNameMap()[attr_9Name] : 0.9}})

            # 10_keraba Field Adding
            pr_10 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr_10))
            pr_10.addAttributes([QgsField("10_keraba", QVariant.Double)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr_10))

            for feat_10 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat_10))

                kerabaIndex = self.dlg.kerabaBox.currentIndex()

                attr_10Name = '10_keraba'
                if kerabaIndex == 0:
                    pr_10.changeAttributeValues({feat_10.id() : {pr_10.fieldNameMap()[attr_10Name] : 0.1}})
                elif kerabaIndex == 1:
                    pr_10.changeAttributeValues({feat_10.id() : {pr_10.fieldNameMap()[attr_10Name] : 0.2}})
                elif kerabaIndex == 2:
                    pr_10.changeAttributeValues({feat_10.id() : {pr_10.fieldNameMap()[attr_10Name] : 0.3}})

            # 11yaneatu Field Adding
            pr11 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr11))
            pr11.addAttributes([QgsField("11yaneatu", QVariant.Double)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr11))

            for feat11 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat11))

                yaneatuIndex = self.dlg.yaneatuBox.currentIndex()

                attr11Name = '11yaneatu'
                if yaneatuIndex == 0:
                    pr11.changeAttributeValues({feat11.id() : {pr11.fieldNameMap()[attr11Name] : 0.1}})
                elif yaneatuIndex == 1:
                    pr11.changeAttributeValues({feat11.id() : {pr11.fieldNameMap()[attr11Name] : 0.2}})
                elif yaneatuIndex == 2:
                    pr11.changeAttributeValues({feat11.id() : {pr11.fieldNameMap()[attr11Name] : 0.3}})

            # 12zoning Field Adding
            pr12 = aLayer.dataProvider()
            # self.dlg.textBrowser.setText(str(pr12))
            pr12.addAttributes([QgsField("12zoning", QVariant.Int)])
            aLayer.updateFields()
            # self.dlg.textBrowser.setText(str(pr12))

            for feat12 in aLayer.getFeatures():
                # self.dlg.textBrowser.setText(str(feat12))

                zoningIndex = self.dlg.zoningBox.currentIndex()

                attr12Name = '12zoning'
                if zoningIndex == 0:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 0}})
                elif zoningIndex == 1:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 1}})
                elif zoningIndex == 2:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 2}})
                elif zoningIndex == 3:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 3}})
                elif zoningIndex == 4:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 4}})
                elif zoningIndex == 5:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 5}})
                elif zoningIndex == 6:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 6}})
                elif zoningIndex == 7:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 7}})
                elif zoningIndex == 8:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 8}})
                elif zoningIndex == 9:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 9}})
                elif zoningIndex == 10:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 10}})
                elif zoningIndex == 11:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 11}})
                elif zoningIndex == 12:
                    pr12.changeAttributeValues({feat12.id() : {pr12.fieldNameMap()[attr12Name] : 12}})

            for i in range(1, 10):
                aLayer.dataProvider().deleteAttributes([1])

            aLayer.endEditCommand()
            aLayer.commitChanges()
            aLayer.updateExtents()

            # self.dlg.textBrowser.setText(str(self.fields[11]))

            # pass
