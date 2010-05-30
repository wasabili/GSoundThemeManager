#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import os
import os.path
from multiprocessing import Process
import pygtk
import gtk
from lib.gstmconsts import *
from lib.gstmcore import *
from lib.gconfhandler import *
from lib.gstmdata import *
DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
UI_PATH = os.path.join(DATA_DIR, 'gstmanager.ui')





class GSoundThemeManager(object):


    def __init__(self):
        os.path.exists(LOCAL_SOUND_DIR) or os.mkdir(LOCAL_SOUND_DIR)    # Create a directory

        self.event_guard = False

        self.init_gui()

        self.create_db()

        self.create_gui()

        self.load_gconf()

        self['mainwindow'].show_all()



    def init_gui(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_PATH)
        self.auto_connects()



    def create_db(self):
        self.db = GSTMdata(self['ls_themes'], self['cmb_themes'])



    def create_gui(self):
        self.oggfilter = gtk.FileFilter()
        self.oggfilter.set_name('Ogg/WAV files')
        self.oggfilter.add_pattern('*.oga')
        self.oggfilter.add_pattern('*.ogg')
        self.oggfilter.add_pattern('*.wav')
        self.allfilter = gtk.FileFilter()
        self.allfilter.set_name('All files')
        self.allfilter.add_pattern('*')
        self.addsoundchooser(self['main_table'], MAIN_EVENT_SOUNDS)
        self.addsoundchooser(self['extra_table'], EXTRA_EVENT_SOUNDS)



    def load_gconf(self):
        self.gconf = GConfHandler()
        curtheme   = self.gconf.get(GCONF_CURRENT_THEME)
        feedback   = self.gconf.get_bool(GCONF_FEEDBACK)

        # Feedback of Windows and Buttons
        self['chk_winbtn_sounds'].set_active(feedback)

        # Current Sound Theme
        theme_id = self.db.get_theme_id(name=curtheme)
        theme_id and self.select_cmb(theme_id)




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
            self.db.set_fc(fc, sound_id)
            self.db.set_cb(checkbutton, sound_id)
            self.db.set_preview(preview, sound_id)




    def reload_soundchoosers(self):
        theme_id = self.db.get_current_theme_id()
        for sound_id in self.db.get_sound_ids():
            path = self.db.get_path(theme_id, sound_id)
            if path:
                self.db.get_fc(sound_id).set_filename(path)
                self.db.get_cb(sound_id).set_active(True)
                self.db.get_preview(sound_id).set_sensitive(True)
            else:
                self.db.get_fc(sound_id).unselect_all()
                self.db.get_cb(sound_id).set_active(False)
                self.db.get_preview(sound_id).set_sensitive(False)
















    def on_cmb_themes_changed(self, widget, *args):
        if self.event_guard:
            self.do_with_cmb_safe(self.reload_soundchoosers)

        theme_id = self.db.get_current_theme_id()
        if theme_id is not None:
            self['btn_remove_theme'].set_sensitive(self.db.is_local(theme_id))




    def on_btn_add_theme_clicked(self, widget, *args):
        self.db.add_new_custom_theme(autoselect=True)




    def on_btn_remove_theme_clicked(self, widget, *args):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO)
        dialog.set_transient_for(self['mainwindow'])
        dialog.set_markup('You can not be undone removing a theme.\nContinue?')
        answer = dialog.run()
        dialog.destroy()
        if answer == gtk.RESPONSE_YES:
            theme_id = self.db.get_current_theme_id()
            if self.db.exists(theme_id):
                result = removetheme(self.db.get_top(theme_id))
                if not result:
                    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                    dialog.set_transient_for(self['mainwindow'])
                    dialog.set_markup('Error while removing the old theme...:'+str(e))
                    dialog.run()
                    dialog.destroy()
            
            self.do_with_cmb_safe(self.db.remove_theme, theme_id)

            self['cmb_themes'].set_active(0)





    def on_fc_file_set(self, widget, *args):
        if self.event_guard: return

        curfol = widget.get_current_folder()
        for sound_id in self.db.get_sound_ids():
            fc = self.db.get_fc(sound_id)
            fc.get_filename() or fc.set_current_folder(curfol)

        self.db.get_preview(sound_id).set_sensitive(bool(widget.get_filename()))
        
        theme_id = self.db.get_current_theme_id()
        sound_id = self.db.get_sound_id(fc=widget)
        filaname = widget.get_filename()
        if self.db.get_path(theme_id, sound_id) != filename:
            if self.db.exists(theme_id):
                self.do_with_cmb_safe(self.db.add_new_custom_theme, True, True)
            else:
                self.db.set_path(theme_id, sound_id, filename)
        




    def on_cb_toggled(self, widget, *args):
        if self.event_guard: return

        sound_id = self.db.get_sound_id(cb=widget)
        fc = self.db.get_fc(sound_id)
        pr = self.db.get_preview(sound_id)

        fc.set_sensitive(widget.get_active())
        pr.set_sensitive(bool(widget.get_active() and fc.get_filename()))

        theme_id = self.db.get_current_theme_id()
        sound_id = self.db.get_sound_id(cb=widget)
        filename = fc.get_filename()
        if filename:
            if self.db.exists(theme_id):
                self.do_with_cmb_safe(self.db.add_new_custom_theme, True, True)
            else:
                self.db.set_path(theme_id, sound_id, filename if widget.get_active() else None)





    def on_btn_preview_clicked(self, widget, *args):
        sound_id  = self.db.get_sound_id(preview=widget)
        soundfile = self.db.get_fc(sound_id).get_filename()

        # play
        p = Process(target=self.preview_sound, args=(soundfile, ))
        p.start()





    def on_chk_winbtn_sounds_toggled(self, widget, *args):
        self.gconf.set_bool(GCONF_FEEDBACK, widget.get_active())





    def on_btn_apply_clicked(self, widget, *args):
        theme_id = self.db.get_current_theme_id()
        title    = self.db.get_name(theme_id)

        if not self.db.exists(theme_id):
            if not self.savetheme(theme_id, title):
                return

        self.gconf.set(GCONF_CURRENT_THEME, title.lower())





    def on_btn_save_as_clicked(self, widget, *args):

        def getText():
            def responseToDialog(entry, dialog, response):
                dialog.response(response)

            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
            dialog.set_transient_for(self['mainwindow'])
            dialog.set_markup('Please enter a <b>new name</b>:')
            dialog.format_secondary_markup("This will be used for a <i>new theme</i> you have created now")

            #create the text input field
            entry = gtk.Entry()
            entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)

            #create a horizontal box to pack the entry and a label
            hbox = gtk.HBox()
            hbox.pack_start(gtk.Label("Name:"), False, 6, 6)
            hbox.pack_end(entry)

            #add it and show it
            dialog.vbox.pack_end(hbox, True, True, 0)
            dialog.show_all()

            #go go go
            dialog.run()
            text = entry.get_text()
            dialog.destroy()
            return text

        newname = getText()
        if self.db.get_theme_id(name=newname):
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self['mainwindow'])
            dialog.set_markup('The same theme already exists.')
            dialog.run()
            dialog.destroy()
            return

        import re
        if not re.match('^[a-zA-Z0-9_]+$', newname):
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self['mainwindow'])
            dialog.set_markup('You can use only latin charactars, numbers and underbar.')
            dialog.run()
            dialog.destroy()
            return

        if newname:
            theme_id = self.db.get_current_theme_id()
            if self.db.exists(theme_id) and self.db.is_local(theme_id):
                overwriteindextheme(self.db.get_top(theme_id), newname)
            else:
                self.savetheme(theme_id, newname)
            self.db.set_name(theme_id, newname)





    def on_btn_install_clicked(self, widget, *args):
        dialog = gtk.FileChooserDialog(title=None, parent=None, action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None)
        dialog.set_transient_for(self['mainwindow'])
        dialog.set_current_folder(DEFAULT_DIR)
        result = dialog.run()
        theme = dialog.get_filename()
        dialog.destroy()

        if result == gtk.RESPONSE_OK:
            result = installtheme(theme)
            if result is None:
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK)
                dialog.set_transient_for(self['mainwindow'])
                dialog.set_markup('Incorrect file format!')
                result = dialog.run()
                dialog.destroy()
                return
            else:
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFORMATION, buttons=gtk.BUTTONS_OK)
                dialog.set_transient_for(self['mainwindow'])
                dialog.set_markup('Imported successfully!')
                result = dialog.run()
                dialog.destroy()
                
                theme_id = self.db._append_theme(*result)
                self.db.select_cmb_by_theme_id(theme_id)


         

    def gtk_main_quit(self, *args):
        if self.gconf.get(GCONF_CURRENT_THEME) == self.db.get_name(self.db.get_current_theme_id()).lower():
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












    def select_cmb(self, theme_id):
        self.db.select_cmb_by_theme_id(theme_id)
        self['btn_remove_theme'].set_sensitive(self.db.is_local(theme_id))





    def savetheme(self, theme_id, title):
        dist = os.path.join(LOCAL_SOUND_DIR, title)
        if os.path.exists(dist):
            result = removetheme(dist)
            if not result:
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                dialog.set_transient_for(self['mainwindow'])
                dialog.set_markup('Error while applying new theme...')
                dialog.run()
                dialog.destroy()
                return False

        result = createtheme(title, self.db.get_dic(theme_id))

        if not result:
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self['mainwindow'])
            dialog.set_markup(output or 'Failed to apply new theme')
            dialog.run()
            dialog.destroy()
            return False

        return True




    def do_with_cmb_safe(self, func, *args):
        self.event_guard = True
        func(*args)
        self.event_guard = False




    def preview_sound(self, filename):
        os.system('canberra-gtk-play --file={0}'.format(filename))




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





