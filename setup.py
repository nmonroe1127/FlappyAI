from cx_Freeze import setup, Executable


base = None

executables = [Executable("game_menu.py", base=None)]

packages = ["idna", "pygame", "os", "neat", "pickle"]
include_files = ["./GameOptions/", "./AIConfigurations/", "./Objects/", "./Images/", "./HighScoreFiles/"]

options = {
    'build_exe': {
        'packages': packages,
        'include_files': include_files,
    },
}

setup(
    name = "Nick and Betsy",
    options = options,
    version = "1.0",
    description = 'Flappy AI',
    executables = executables
)