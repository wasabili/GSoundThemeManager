import os
from distutils.core import setup

setup(name='gsoundthememanager',
      version='1.1.0a1',
      description='Customize you desktop sound theme',
      author='Yuichi Nishiwaki',
      author_email='ffiannkks@gmail.com',
      url='http://github.com/wasabili/GSoundThemeManager',
      scripts=os.listdir('scripts'),
      py_modules=['src/gstmanager'],
      packages=['lib'],
      package_dir={'lib':'src/lib'},
      data_files=[('data', ['data/gstmanager.ui'])],
      )
