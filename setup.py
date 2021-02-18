from setuptools import setup
from os import path

cwd = path.abspath(path.dirname(__file__))
with open(path.join(cwd, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
        name="cliutils",
        version="2.4.1",
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
                "reload-screens=cliutils:reload_screens.main",
                "themer=cliutils:themer.main",
                "qtile-ws=cliutils:qtile_ws.main",
                "i3-change-wall=cliutils:i3_change_wall.main",
                "aucli=cliutils:audio._cliEntry",
                "mcc=cliutils:musikcubeClient.main"
                ]
            },
        python_requires=">=3.6, <4",
        install_requires=["PyYAML","pywal","websockets", "aiohttp"]
        )
