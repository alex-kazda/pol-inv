from setuptools import setup

setup(
    name='pol-inv',
    version='0.1.0',
    packages=['pol_inv'],
    url='',
    license='MIT',
    author='Alexandr Kazda',
    author_email='alex.kazda@gmail.com',
    install_requires=[
        'python-sat'
    ],
    description='Package for computing polymorphisms and invariant relations in universal algebra'
)
