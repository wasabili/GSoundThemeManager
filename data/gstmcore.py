#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

from gstmconsts import *

def salvagetheme(location):
    
    index = location+'/index.theme'
    
    if not os.path.exists(index):
        return None
    
    dic = {}
    
    # load index.theme
    with open(index, 'r') as f:
        from ConfigParser import ConfigParser
        config = ConfigParser()
        config.readfp(f)
        name = config.get('Sound Theme', 'Name')
        dirs = config.get('Sound Theme', 'Directories').split(' ')
        for dir in dirs:
            profile = config.get(dir, 'OutputProfile')
            if profile == 'stereo':
                stereo = dir
                break
            else:
                return None
        for root, dirs, files in os.walk(location+'/'+stereo):
            for file in files:
                if file.split('.')[-1] in ('ogg', 'wav', 'oga', 'sound'):
                    id = ''.join(file.split('.')[:-1])
                    dic[id] = root+'/'+file
                
    return name, dic
        
def findthemes():
    if not os.path.exists(LOCAL_SOUND_DIR):
        os.mkdir(LOCAL_SOUND_DIR)
    for parent in [SOUND_DIR, LOCAL_SOUND_DIR]:
        for child in os.listdir(parent):
            path = parent + '/' + child
            value = salvagetheme(path)
            if value:
                yield parent == LOCAL_SOUND_DIR, path, value[0], value[1]


def removetheme(top=None):
    try:
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)
        return True
        
    except OSError, e:
        print >>sys.stderr, 'Error while removing a theme:'+str(e)
        return False

import shutil

indextmpl = """
[Sound Theme]
Name=name
Directories=stereo

[stereo]
OutputProfile=stereo
"""


def createtheme(name, sounds):
    global indextmpl

    start = os.getcwd()
    os.chdir(os.path.abspath(LOCAL_SOUND_DIR))

    try:
        if os.path.exists(name):
            print >> sys.stderr, 'The same name directory already exists.'
            raise OSError
        os.mkdir(name)
        os.chdir(name)

        spec = indextmpl.replace("name", name)

        index = open('index.theme', 'w')
        index.write(spec)
        index.close()

        os.mkdir('stereo')

        os.chdir('../')

        for spec, sound in sounds.items():

            print sound, 'to', spec

            target = os.path.abspath(sound)
            extension = sound.split('.')[-1]
            dist = os.path.abspath('./'+name+'/stereo/'+spec+'.'+extension)

            shutil.copy(target, dist)

    except OSError, e:
        print >> sys.stderr, 'It\'s not permitted to write to the target.'
        return False
    except IOError, e:
        print >> sys.stderr, 'An error occurred while processing: ', e.args[1]
        return False
    else:
        return True
    finally:
        os.chdir(start)

def overwriteindextheme(top, name):
    global indextmpl

    start = os.getcwd()
    os.chdir(os.path.abspath(top))

    try:
        os.remove('index.theme')

        spec = indextmpl.replace("name", name)

        index = open('index.theme', 'w')
        index.write(spec)
        index.close()

    except OSError, e:
        print >> sys.stderr, 'It\'s not permitted to write to the target.'
        return False
    except IOError, e:
        print >> sys.stderr, 'An error occurred while processing: ', e.args[1]
        return False
    else:
        return True
    finally:
        os.chdir(start)

