#!/usr/bin/env python3
import os

from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


PLUGIN_ENTRY_POINT = 'ovos-solver-hivemind-plugin=ovos_hivemind_solver:HiveMindSolver'
setup(
    name='ovos-solver-hivemind-plugin',
    version="0.0.0",
    description='A question solver plugin for OVOS',
    url='https://github.com/JarbasHiveMind/ovos-solver-hivemind-plugin',
    author='jarbasai',
    author_email='jarbasai@mailfence.com',
    license='MIT',
    packages=['ovos_hivemind_solver'],
    zip_safe=True,
    keywords='OVOS openvoiceos plugin utterance fallback query',
    entry_points={'neon.plugin.solver': PLUGIN_ENTRY_POINT},
    install_requires=required("requirements.txt"),
    long_description_content_type='text/markdown'
)
