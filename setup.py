from setuptools import find_packages, setup

setup(name='pykeepassxc',
      version='0.1',
      description='A Python wrapper around the keepassxc-cli command.',
      url='https://github.com/nepoh/pykeepassxc',
      author='Nepoh',
      author_email='hello@nepoh.eu',
      license='MIT',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      install_requires=[
          'pexpect',
      ],
      tests_require=[
          'parameterized',
          'lxml',
      ],
      zip_safe=False)
