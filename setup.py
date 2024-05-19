from setuptools import setup, find_packages

setup(
    name='panda_rl_envs',
    version='0.0.0',
    description='Envs/tasks for RL with a real Panda and Polymetis from FAIR.',
    author='Trevor Ablett',
    packages=find_packages(),
    install_requires=[
        'polymetis',
        'panda_polymetis',
        'transform_utils',
        'pymodbus==2.5.3',  # should have been installed by polymetis
        'gym<=0.23'
    ],
    include_package_data=True
)