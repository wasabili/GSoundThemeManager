#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
except:
    print >> sys.stderr, "Error: PyGTK not installed"
    sys.exit(1)

if gtk.pygtk_version < (2,12,0):
    errtitle = "Error"
    errmsg = "PyGTK 2.12.0 or later required"
    if gtk.pygtk_version < (2,4,0):
        print >> sys.stderr, errtitle + ": " + errmsg
    else:
        errdlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK)
        errdlg.set_title(errtitle)
        errdlg.set_markup(errmsg)
        errdlg.run()
    sys.exit(1)

import os.path
import pygame

# MY DATA
DATA_DIR = os.path.join(os.getcwd(), 'data')
sys.path.insert(0, DATA_DIR)
from gstmconsts import *
from gstmcore import *
from gconfhandler import *
from gstmdata import *
UI_PATH = os.path.join(DATA_DIR, 'gstmanager.ui')


class GSoundThemeManager(object):

    # The first element must be 'Customized'
    customnames = ['Customized']

    def __init__(self):
        """Initializer"""

        # manage flags
        self.reloadfcs = True

        # load GUI
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_PATH)
        self.auto_connects()

        # DATA
        self.data = GSTMdata(self['ls_themes'], self['cmb_themes'])
        self.gconf = GConfHandler()
        pygame.mixer.pre_init(44100, -16, 2, 1024*3)
        pygame.init()

        # filters
        self.oggfilter = gtk.FileFilter()
        self.oggfilter.set_name('Ogg/WAV files')
        self.oggfilter.add_pattern('*.oga')
        self.oggfilter.add_pattern('*.ogg')
        self.oggfilter.add_pattern('*.wav')
        self.allfilter = gtk.FileFilter()
        self.allfilter.set_name('All files')
        self.allfilter.add_pattern('*')

        # setup GUI
        self.addsoundchooser(self['main_table'], MAIN_EVENT_SOUNDS)
        self.addsoundchooser(self['extra_table'], EXTRA_EVENT_SOUNDS)

        # load current status
        feedback = self.gconf.get_bool(GCONF_FEEDBACK)
        curtheme = self.gconf.get(GCONF_CURRENT_THEME)
        self['chk_winbtn_sounds'].set_active(feedback)
        self['cmb_themes'].set_active_iter(self.data.get_iter_from_theme_id(self.data.get_theme_id(name=curtheme)))
        self.loadtheme()

        # start
        self['mainwindow'].show_all()


    def addsoundchooser(self, table, events):

        table.resize(len(events), 2)
        for i, event in enumerate(events):
            
            if event is None:
                sep = gtk.HSeparator()
                table.attach(sep, 0, 3, i, i+1, yoptions=gtk.SHRINK)
                continue
            
            sound_id = event[0]
            label = event[1]
            
            # Checkbutton
            checkbutton = gtk.CheckButton(label)
            checkbutton.connect('toggled', self.on_cb_toggled)

            # FileChooserButton
            fc = gtk.FileChooserButton(title='')
            fc.connect('file-set', self.on_fc_file_set)
            fc.set_current_folder(DEFAULT_DIR)
            fc.add_filter(self.oggfilter)
            fc.add_filter(self.allfilter)
            fc.set_filter(self.oggfilter)
            fc.set_sensitive(False)
            
            # Preview Button
            preview = gtk.Button()
            icon = gtk.Image()
            icon.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
            preview.set_image(icon)
            preview.connect('clicked', self.on_btn_preview_clicked)
            
            # attach to table
            table.attach(checkbutton, 0, 1, i, i+1, yoptions=gtk.SHRINK)
            table.attach(fc, 1, 2, i, i+1, yoptions=gtk.SHRINK)
            table.attach(preview, 2, 3, i, i+1, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)

            # add to data
            self.data.set_fc(fc, sound_id)
            self.data.set_cb(checkbutton, sound_id)
            self.data.set_preview(preview, sound_id)

    def _loadfcs(self, theme_id):
        # cb, fc, previews
        for sound_id in self.data.get_sound_ids():
            path = self.data.get_path(theme_id, sound_id)
            if path:
                self.data.get_fc(sound_id).set_filename(path)
                self.data.get_cb(sound_id).set_active(True)
                self.data.get_preview(sound_id).set_sensitive(True)
            else:
                self.data.get_fc(sound_id).unselect_all()
                self.data.get_cb(sound_id).set_active(False)
                self.data.get_preview(sound_id).set_sensitive(False)

    def loadtheme(self):
        theme_id = self.data.get_current_theme_id()
        self._loadfcs(theme_id)

        # remove-button
        self['btn_remove_theme'].set_sensitive(self.data.is_local(theme_id))


    def on_cmb_themes_changed(self, widget, *args): # TODO confirm if add/remove theme action doesnt triggers something wrong
        theme_id = self.data.get_current_theme_id()

        if self.reloadfcs:
            self._loadfcs(theme_id)

        # remove-button
        self['btn_remove_theme'].set_sensitive(self.data.is_local(theme_id))

    def on_btn_add_theme_clicked(self, widget, *args):
        count = len(self.customnames)
        title = 'Untitled%d' % count
        self.customnames.append(title)
        theme_id = self.data.add_theme(title, {}, False)
        self['cmb_themes'].set_active_iter(self.data.get_iter_from_theme_id(theme_id))

    def on_btn_remove_theme_clicked(self, widget, *args):

        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO)
        dialog.set_transient_for(self['mainwindow'])
        dialog.set_markup('You can not be undone removing a theme.\nContinue?')
        answer = dialog.run()
        dialog.destroy()
        if answer == gtk.RESPONSE_YES:
            top = self.data.get_top_dir(self.data.get_current_theme_id())            
            result = removetheme(top)
            if not result:
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                dialog.set_transient_for(self['mainwindow'])
                dialog.set_markup('Error while removing the old theme...:'+str(e))
                dialog.run()
                dialog.destroy()
            
            self.data.remove_theme(self.get_current_theme_id())
            self['cmb_themes'].set_active(0)

    def on_fc_file_set(self, widget, *args):

        # share location
        curfol = widget.get_current_folder()
        for sound_id in self.data.get_sound_ids():
            fc = self.data.get_fc(sound_id)
            fc.get_filename() or fc.set_current_folder(curfol)
    
        theme_id = self.data.get_current_theme_id()
        sound_id = self.data.get_sound_id(fc=widget)

        # preview widget
        if widget.get_filename():
            self.data.get_preview(sound_id).set_sensitive(True)
        else:
            self.data.get_preview(sound_id).set_sensitive(False)
        
        # custom
        if self.data.get_path(theme_id, sound_id) != widget.get_filename():
            self.set_as_customized(self.get_current_states())
        
    def on_cb_toggled(self, widget, *args):

        sound_id = self.data.get_sound_id(cb=widget)
        fc = self.data.get_fc(sound_id)
        fc.set_sensitive(widget.get_active())
        pr = self.data.get_preview(sound_id)
        pr.set_sensitive(bool(widget.get_active() and fc.get_filename()))

        # custom
        sound_id = self.data.get_sound_id(cb=widget)
        fc_status = self.data.get_fc(sound_id).get_filename()
        if fc_status:
            self.set_as_customized(self.get_current_states())

    def on_btn_preview_clicked(self, widget, *args):
        sound_id = self.data.get_sound_id(preview=widget)
        fc = self.data.get_fc(sound_id)
        soundfile = fc.get_filename()

        # play
        sound = pygame.mixer.Sound(soundfile)
        sound.play()

    def on_chk_winbtn_sounds_toggled(self, widget, *args):
        self.gconf.set_bool(GCONF_FEEDBACK, widget.get_active())

    def on_btn_apply_clicked(self, widget, *args):

        theme_id = self.data.get_current_theme_id()
        title = self.data.get_name(theme_id)

        if title in self.customnames or not self.data.exists(theme_id):

            # --Overwrite?--------------------------
            dist = os.path.join(LOCAL_SOUND_DIR, title)
            if os.path.exists(dist):
                result = removetheme(dist)
                if not result:
                    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                    dialog.set_transient_for(self['mainwindow'])
                    dialog.set_markup('Error while applying new theme...')
                    dialog.run()
                    dialog.destroy()
                    return

            # --Execute------------------------------
            result = createtheme(title, self.data.get_dic(theme_id))

            if not result:
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                dialog.set_transient_for(self['mainwindow'])
                dialog.set_markup(output or 'Failed to apply new theme')
                dialog.run()
                dialog.destroy()

        self.gconf.set(GCONF_CURRENT_THEME, title.lower())

    def gtk_main_quit(self, *args):
        if self.gconf.get(GCONF_CURRENT_THEME) == self.data.get_name(self.data.get_current_theme_id()).lower():
            self['mainwindow'].hide_all()
            gtk.main_quit()
        else:
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK_CANCEL)
            dialog.set_transient_for(self['mainwindow'])
            dialog.set_markup('The new theme is not saved.\nExit?')
            result = dialog.run()
            dialog.destroy()
            if result == gtk.RESPONSE_OK:
                self['mainwindow'].hide_all()
                gtk.main_quit()

    def get_current_states(self):
        sound_ids = self.data.get_sound_ids()
        base_dic = self.data.get_dic(self.data.get_current_theme_id())
        for sound_id in sound_ids:
            cb = self.data.get_cb(sound_id)
            fc = self.data.get_fc(sound_id)
            sound = fc.get_filename()
            if cb.get_active() and sound:
                base_dic[sound_id] = sound
            else:
                if sound_id in base_dic:
                    del base_dic[sound_id]
        return base_dic

    def set_as_customized(self, dic):

        self.reloadfcs = False

        theme_id = self.data.get_current_theme_id()

        customized = bool(self.data.get_name(theme_id) in self.customnames)
        existing = self.data.get_theme_id_with_exceptions(dic, self.customnames)

        if existing:
            self['cmb_themes'].set_active_iter(self.data.get_iter_from_theme_id(existing)) # TODO confirm asdflhasdga...
        elif customized:
            self.data.set_dic(theme_id, dic)
        else:
            custom_theme_id = self.data.get_theme_id(name=self.customnames[0])
            if custom_theme_id is None:
                custom = self.data.add_theme(self.customnames[0], dic, False)
                self['cmb_themes'].set_active_iter(self.data.get_iter_from_theme_id(custom)) # TODO confirm asdflhasdga...
            else:
                self.data.set_dic(custom_theme_id, dic)
                self['cmb_themes'].set_active_iter(self.data.get_iter_from_theme_id(custom_theme_id)) # TODO confirm asdflhasdga...

        self.reloadfcs = True

    def __getitem__(self, key):
        return self.builder.get_object(key)

    def auto_connects(self):
        event_handlers = {}
        for (itemname, value) in self.__class__.__dict__.items():
            if callable(value):
                event_handlers[itemname] = getattr(self, itemname)
        self.builder.connect_signals(event_handlers)

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = GSoundThemeManager()
    app.main()
