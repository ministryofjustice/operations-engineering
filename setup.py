from setuptools import find_packages, setup

# This allows us to install the package outside of the repository using the following command:
# pip install git+https://github.com/ministryofjustice/operations-engineering.git
setup(
    name='operations-engineering',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.9.4',
        'boto3==1.34.84',
        'cryptography==42.0.5',
        'gql==3.5.0',
        'notifications-python-client==9.0.0',
        'pyaml-env==1.2.1',
        'pygithub==2.3.0',
        'pyjwt==2.8.0',
        'python-dateutil==2.8.2',
        'requests==2.31.0',
        'slack-sdk==3.27.1',
        'toml==0.10.2',
    ],
    extras_require={
        'dev': [
            'coverage==7.4.4',
            'freezegun==1.4.0',
            'moto==5.0.5',
            'pytest==8.1.1',
            'requests-mock==1.12.1',
        ],
    },
    include_package_data=True,
    description=(
        'The operations-engineering package provides a suite of tools and services developed by the '
        'Operations Engineering team at the Ministry of Justice. This package is designed to support '
        'the development, deployment, and maintenance of digital services within the department. '
        'It includes modules for interacting with GitHub, sending notifications, handling configuration '
        'via environment variables, and more, ensuring that digital projects are delivered efficiently, '
        'securely, and with high quality.'
    ),

    author='Ministry of Justice',
    author_email='operations-engineering@digital.justice.gov.uk',
    url='https://github.com/ministryofjustice/operations-engineering',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)
