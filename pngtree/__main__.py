from sqlite3 import connect
from pathlib import Path
from . import tree
import time

# t = tree.PNGTree(connection=connect('images.sqlite'))
# for file in (Path.home() / 'Pictures' / 'portraits').iterdir():
# 	t.insert_image(file.open('rb'))
# t.close()

t = tree.PNGTree(connection=connect('images.sqlite'))
with open('ree.png', 'wb') as f:
	t.get_image(f, 400)
