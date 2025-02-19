from setuptools import setup, find_packages

setup(
    name='index',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Lista de dependencias
    ],
    entry_points={
        'console_scripts': [
            'mi_comando=generar_codigo.app:main',  # Ajusta según tu estructura
        ],
    },
)
