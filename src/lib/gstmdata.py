#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gstmconsts import *
from gstmcore import findthemes

class GSTMdata(object):

    theme_ids = []

    id_islocal = {}
    id_top = {}
    id_name = {}
    id_dic = {}
    id_existance = {}
    
    islocal_id = {}
    top_id = {}
    name_id = {}
    dic_id = {}
    existance_id = {}

    sound_ids = set([])

    id_fc = {}
    id_cb = {}
    id_preview = {}

    fc_id = {}
    cb_id = {}
    preview_id = {}

    def __init__(self, liststore, combobox):
        self.combobox = combobox
        self.liststore = liststore
        self.treemodel = combobox.get_model()

        # islocal, top, name, dic
        for islocal, top, name, dic in findthemes():
            self._append_theme(islocal, top, name, dic, True)

        self.custom_theme_num = 0

    def get_sound_ids(self):
        return self.sound_ids.copy()

    def get_theme_ids(self):
        return self.theme_ids.copy()


    def get_current_theme_id(self):
        active_iter = self.combobox.get_active_iter()
        if active_iter is None:
            return None
        else:
            return self.treemodel.get_string_from_iter(active_iter)

    def get_iter_from_theme_id(self, theme_id):
        return self.treemodel.get_iter_from_string(theme_id)

    def get_theme_id(self, name=None, dic=None):
        if name is not None:
            for key in self.name_id.iterkeys():
                if key.lower() == name.lower():
                    return self.name_id[key]
        if dic is not None:
            for value in self.id_dic.itervalues():
                if value == dic:
                    return self.dic_id[id(value)]

    def get_theme_id_with_exceptions(self, dic, exceptions):
        if dic is not None:
            for theme_id, value in self.id_dic.iteritems():
                if value == dic and (self.get_name(theme_id).lower() not in [x.lower() for x in exceptions]):
                    return self.dic_id[id(value)]

    def get_sound_id(self, fc=None, cb=None, preview=None):
        if fc is not None:
            return self.fc_id[fc]
        if cb is not None:
            return self.cb_id[cb]
        if preview is not None:
            return self.preview_id[preview]

    def get_fc(self, sound_id):
        return self.id_fc[sound_id]

    def get_cb(self, sound_id):
        return self.id_cb[sound_id]

    def get_preview(self, sound_id):
        return self.id_preview[sound_id]

    def set_fc(self, fc, sound_id):
        self.id_fc[sound_id] = fc
        self.fc_id[fc] = sound_id
        self.sound_ids.add(sound_id)

    def set_cb(self, cb, sound_id):
        self.id_cb[sound_id] = cb
        self.cb_id[cb] = sound_id
        self.sound_ids.add(sound_id)

    def set_preview(self, preview, sound_id):
        self.id_preview[sound_id] = preview
        self.preview_id[preview] = sound_id
        self.sound_ids.add(sound_id)

    def get_path(self, theme_id, sound_id):
        dic = self.get_dic(theme_id)
        return dic.get(sound_id)

    def set_path(self, theme_id, sound_id, path):
        dic = self.get_dic(theme_id)
        if path is None:
            del dic[sound_id]
        else:
            dic[sound_id] = path
        self.set_dic(theme_id, dic)

    def _append_theme(self, islocal, top, name, dic, existance=True):
        theme_id = self.treemodel.get_string_from_iter(self.liststore.append((name,)))

        self.theme_ids.append(theme_id)

        self.islocal_id[islocal] = theme_id
        self.top_id[top] = theme_id
        self.name_id[name] = theme_id
        self.dic_id[id(dic)] = theme_id
        self.existance_id[existance] = theme_id

        self.id_islocal[theme_id] = islocal
        self.id_top[theme_id] = top
        self.id_name[theme_id] = name
        self.id_dic[theme_id] = dic
        self.id_existance[theme_id] = existance

        return theme_id

    def add_theme(self, name, dic, existance):
        return self._append_theme(True, None, name, dic, existance)

    def remove_theme(self, theme_id):
        orig_theme_id = theme_id

        self.liststore.remove(self.treemodel.get_iter_from_string(orig_theme_id))

        # theme_id, islocal, top, name, dic, existance
        themes = []
        tmp = None
        prev = None
        flag = False
        for theme_id in self.theme_ids:
            if theme_id == orig_theme_id:
                flag = True
                prev = theme_id
 
            if flag:
                tmp = prev
                prev = theme_id
            else:
                tmp = theme_id


            islocal = self.id_islocal[tmp]
            top = self.id_top[tmp]
            name = self.id_name[tmp]
            dic = self.id_dic[tmp]
            existance = self.id_existance[tmp]

            themes.append((tmp, islocal, top, name, dic, existance))

        self.islocal_id.clear()
        self.top_id.clear()
        self.name_id.clear()
        self.dic_id.clear()
        self.existance_id.clear()

        self.id_islocal.clear()
        self.id_top.clear()
        self.id_name.clear()
        self.id_dic.clear()
        self.id_existance.clear()

        self.theme_ids.remove(orig_theme_id)
        for theme_id, islocal, top, name, dic, existance in themes:    
            self.islocal_id[islocal] = theme_id
            self.top_id[top] = theme_id
            self.name_id[name] = theme_id
            self.dic_id[id(dic)] = theme_id
            self.existance_id[existance] = theme_id

            self.id_islocal[theme_id] = islocal
            self.id_top[theme_id] = top
            self.id_name[theme_id] = name
            self.id_dic[theme_id] = dic
            self.id_existance[theme_id] = existance

    def get_dic(self, theme_id):
        return self.id_dic[theme_id].copy()

    def get_name(self, theme_id):
        if theme_id is None:
            return ""
        return self.id_name[theme_id]

    def exists(self, theme_id):
        return self.id_existance[theme_id]

    def is_local(self, theme_id):
        return self.id_islocal[theme_id]

    def get_top(self, theme_id):
        return self.id_top[theme_id]

    def set_name(self, theme_id, name):
        oldname = self.id_name[theme_id]
        del self.name_id[oldname]

        self.id_name[theme_id] = name
        self.name_id[name] = theme_id

        theme_iter = self.get_iter_from_theme_id(theme_id)
        self.liststore.set(theme_iter, 0, name)

    def set_dic(self, theme_id, dic):
        olddic = self.id_dic[theme_id]
        del self.dic_id[id(olddic)]

        self.id_dic[theme_id] = dic
        self.dic_id[id(dic)] = theme_id

    def add_new_custom_theme(self, modify=False, autoselect=False):
        self.custom_theme_num += 1
        title = 'Untitled{0}'.format(self.custom_theme_num)
        dic = self.get_current_states() if modify else {}
        theme_id = self.add_theme(title, dic, False)
        if autoselect: self.select_cmb_by_theme_id(theme_id)
        return theme_id

    def select_cmb_by_theme_id(self, theme_id):
        self.combobox.set_active_iter(self.get_iter_from_theme_id(theme_id))

    def get_current_states(self):
        base_dic = self.get_dic(self.get_current_theme_id())
        for sound_id in self.sound_ids:
            cb = self.get_cb(sound_id)
            fc = self.get_fc(sound_id)
            sound = fc.get_filename()
            if cb.get_active() and sound:
                base_dic[sound_id] = sound
            else:
                if sound_id in base_dic:
                    del base_dic[sound_id]
        return base_dic
