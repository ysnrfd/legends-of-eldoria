import py_compile, glob, os

files = glob.glob(os.path.join('rpg_game','**','*.py'), recursive=True)
print(len(files), 'files found')
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print('Error compiling', f, e)
print('Compilation done')
