import os

def list_dirs(base_path, indent=0, max_depth=2):
    if indent > max_depth:
        return
    for item in os.listdir(base_path):
        if item in ['__pycache__', 'migrations', '.venv']:
            continue
        path = os.path.join(base_path, item)
        print('    ' * indent + f'- {item}')
        if os.path.isdir(path):
            list_dirs(path, indent + 1, max_depth)

list_dirs('.', indent=0, max_depth=2)