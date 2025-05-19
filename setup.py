from setuptools import setup

setup(
    name='sqs-list-filled-queues',
    version='0.1',
    py_modules=['sqs-list-filled-queues'],
    install_requires=[
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'sqs-list-filled-queues=sqs-list-filled-queues:main',
        ],
    },
)