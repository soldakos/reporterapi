from pathlib import Path

import plyer

def myfunc(data):
    print('myfunc: ',data)

# print(plyer.filechooser.choose_dir(), multiple=True)
# print(plyer.filechooser.open_file(path=r"d://Projects//reporter-vue", multiple=True, preview=True, on_selection=myfunc))
print(plyer.filechooser.open_file(path=r"d:\Projects\reporter-vue", multiple=True, preview=True, on_selection=myfunc))
