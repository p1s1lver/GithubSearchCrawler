from cx_Freeze import setup, Executable

build_exe_options = {}

setup(
    name="GithubCrawler",
    version="0.1",
    description="crawler demo of github",
    options={"build_exe": build_exe_options},
    executables=[Executable("run.py", base=None)]
)