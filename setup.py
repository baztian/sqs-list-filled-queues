from setuptools import setup

setup(
    name='sqs-list-filled-queues',
    version='0.1',
    py_modules=['sqs_list_filled_queues'],
    install_requires=[
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'sqs-list-filled-queues = sqs_list_filled_queues:main',
        ],
    },
)