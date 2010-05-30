#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path

SOUND_DIR = '/usr/share/sounds'
LOCAL_SOUND_DIR = os.path.join(os.getenv('HOME'), '.local/share/sounds')
DEFAULT_DIR = os.getenv('HOME')

GCONF_FEEDBACK = '/desktop/gnome/sound/input_feedback_sounds'
GCONF_CURRENT_THEME = '/desktop/gnome/sound/theme_name'

# id : label
MAIN_EVENT_SOUNDS = (
('desktop-login', 'Login event'),
('desktop-logout', 'Logout event'),
('dialog-error', 'Error dialog'),
('dialog-warning', 'Warning dialog'),
('dialog-information', 'Information dialog'),
('dialog-question', 'Question dialog'),
('system-ready', 'System ready (GDM startup)')
)

# id : label
EXTRA_EVENT_SOUNDS = (
('button-pressed', 'Press a button'),
('button-toggle-on', 'Activate a check button'),
('button-toggle-off', 'Deactivate a check button'),
('menu-click', 'Click a menu'),
('notebook-tab-changed', 'Change a tab'),
None,
('trash-empty', 'Empty Trash'),
None,
('message-new-instant', 'Recieve a new instant message'),
None,
('window-new', 'Open a new window'),
('window-close', 'Close a window')
)
