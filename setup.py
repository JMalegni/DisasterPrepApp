from setuptools import setup, find_packages

setup(
    name='seele',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=5.0.6',
	'django-bootstrap4>=23.4',
	'sqlparse>=0.3.1'
    ],
    entry_points={
        'console_scripts': [
            'seele_start=seele_app.entrypoint:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    author='Nicholas DeSanctis',
    author_email='nickdesanctis17@gmail.com',
    description='SEELE Web Development server package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JMalegni/DisasterPrepApp',
    project_urls={
        'Source': 'https://github.com/JMalegni/DisasterPrepApp',
    },
)
