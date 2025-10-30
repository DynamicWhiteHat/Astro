from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'gui'

executables = [
    Executable('mainV2.py', base=base, target_name = 'Astro')
]

setup(name='Astro',
      version = '2',
      description = 'An AI-Enabled Voice Assistant For Windows',
      options = {'build_exe': build_options},
      executables = executables)
