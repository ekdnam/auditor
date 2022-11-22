from setuptools import setup

setup(
    name='auditor',
    version='0.1.0',
    packages=['auditor'],
    entry_points={
        'console_scripts': [
            'auditor = auditor.__main__:main'
        ]
    },
    install_requires=[
        'xvfbwrapper',
        'click',
        'selenium',
        'numpy',
        'imagehash',
        'Pillow',
        'python-dotenv'
    ],

)
