from setuptools import setup
import os

def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name='sqs-list-filled-queues',
    version='0.2',
    description="A Python script to monitor and list Amazon SQS " \
    "queues with messages, featuring real-time updates and AWS console links.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/baztian/sqs-list-filled-queues",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
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