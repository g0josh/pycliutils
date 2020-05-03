from setuptools import setup
from os import path

cwd = path.abspath(path.dirname(__file__))
with open(path.join(cwd, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
        name="cliutils",
        version="2.0.0",
        description="A metapackage for all the common CLI utils on jMach2",
        long_description=long_description,
        long_description_content_type="text/markdown",
        license="MIT",
        author="Job",
        author_email="jobin.jj@gmail.com",
        packages=["cliutils"],
        scripts=["bin/utilization", "bin/temp"],
        entry_points={
            "console_scripts":[
                "reload-screens=cliutils:reload_screens",
                "themer=cliutils:themer",
                "qtile-ws=cliutils:qtile_ws",
                "i3-change-wall=cliutils:i3_change_wall",
                "audio=cliutils:audio"
                ]
            },
        python_requires=">=3.6, <4",
        install_requires=["PyYAML","pywal"]
        )
