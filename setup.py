from setuptools import setup, find_packages

setup(
    name='backtesting_custom',
    version='0.1',
    description='Versión personalizada de Backtesting.py',
    author='Tu Nombre',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib'
    ],
    include_package_data=True,
    zip_safe=False
)
