from distutils.core import setup

setup(
    name="tehblog",
    version="1.3",
    url="http://github.com/andrewebdev/tehblog",
    description="A simple django blogging app",
    author="Andre Engelbrech",
    author_email="andre@teh-node.co.za",
    packages=['tehblog'],
    package_dir={'': 'src'},
)
