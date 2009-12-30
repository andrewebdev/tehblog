from setuptools import setup, find_packages

setup(
    name="tehblog",
    version="0.2",
    url="",
    description="A simple django blogging app",
    author="Andre Engelbrech",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'django-tagging',
    ],
)
