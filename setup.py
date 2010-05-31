import os
from distutils.core import setup

setup(name='gstmanager',
      version='1.1.1',
      description='Customize you desktop sound theme',
      author='Yuichi Nishiwaki',
      author_email='ffiannkks@gmail.com',
      url='http://github.com/wasabili/GSoundThemeManager',
      scripts=['scripts/gsoundthememanager'],
      packages=['gstmanager', 'gstmanager.lib'],
      package_data={'gstmanager':['data/gstmanager.ui']},
      data_files=[('share/applications', ['data/gstmanager.desktop'])]
      )
