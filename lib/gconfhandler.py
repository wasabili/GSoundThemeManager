#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gconf
class GConfHandler(object):
    def __init__(self):
        self.client = gconf.client_get_default()

    def get(self, key):
        return self.client.get_string(key)
        
    def set(self, key, value):
        self.client.set_string(key, value)
        
    def get_bool(self, key):
        return self.client.get_bool(key)
        
    def set_bool(self, key, value):
        v = 1 if value else 0
        self.client.set_bool(key, v)
