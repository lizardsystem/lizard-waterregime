from setuptools import setup

version = '0.2'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-staticfiles',
    'django-extensions',
    'lizard-ui',
    'lizard-map >= 1.61',
    'lizard-fewsunblobbed',
    'timeseries',
    'django-nose',
    'pkginfo',
    'south'
    ],

tests_require = [
    ]

setup(name='lizard-waterregime',
      version=version,
      description="TODO",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='TODO',
      author_email='TODO@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_waterregime'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
            ],
          'lizard_map.adapter_class': [
            'adapter_waterregime = lizard_waterregime.layers:AdapterWaterRegime',
            ],
          },
      )
