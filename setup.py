from setuptools import setup, find_packages

setup(
    name='Chess',
    version='1.0.0',
    scripts=['./main.py'],
    description='Chess game with fully implemented GUI and AI',
    url='https://github.com/Bulletukk/Chess_game',
    author='Bulletukk',
    author_email='tootsojahni@anl.gov.kg',
    license='Laissezfaire',
    packages=find_packages(),  # Automatically find packages in your directory
    install_requires=[
        'enum34',  # Use 'enum34' for compatibility with older Python versions
        'pygame',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'chess=main:main',  # Replace with your package and function
        ],
    }
)