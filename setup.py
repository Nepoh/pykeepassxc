from setuptools import setup

setup(name='pykeepassxc',
      version='0.1',
      description='A Python wrapper around the keepassxc-cli command.',
      url='http://github.com/nepoh/pykeepassxc',
      author='Nepoh',
      author_email='me@nepoh.eu',
      license='MIT',
      packages=['pykeepassxc'],
      install_requires=[
          'packaging',
          'pexpect',
      ],
      zip_safe=False)
