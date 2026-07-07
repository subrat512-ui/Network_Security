from setuptools import find_packages, setup
from typing import List

def get_requirements():
    requirements=[]
    try:
        with open('requirements.txt','r') as file:
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                if(requirement and requirement!='-e .'):
                    requirements.append(requirement)
    except FileNotFoundError:
        print("File not Found")
    return requirements
setup(
    name="networsecurity",
    version="0.0.1",
    author="Manan",
    packages=find_packages(),
    install_requires=get_requirements()
)






