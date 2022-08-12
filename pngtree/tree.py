from sqlite3 import Connection, Cursor, connect
from io import BufferedIOBase
from . import png

def fetchval(cursor: Cursor):
	return cursor.fetchone()[0]

class PNGTree:
	def __init__(self, connection: Connection = connect(":memory:")):
		self.conn = connection
		self.conn.executescript(
			"""CREATE TABLE IF NOT EXISTS chunks(
			type CHAR(4) NOT NULL,
			data BLOB NOT NULL,
			crc INT PRIMARY KEY
		);

		CREATE TABLE IF NOT EXISTS images(
			id INT NOT NULL,
			position INT NOT NULL,
			chunk_crc INT NOT NULL,
			FOREIGN KEY (chunk_crc) REFERENCES chunks(crc)
		);"""
		)

	def insert_image(self, f: BufferedIOBase) -> int:
		cur = self.conn.cursor()

		image_id = (
			fetchval(cur.execute("select IFNULL(max(id), 0) from images;")) + 1
		)

		for position, chunk in enumerate(png.unpack_png(f)):
			# https://stackoverflow.com/a/19343100
			# Since crc is unique and is acting as our hash, this should stop dupes from coming in
			cur.execute(
				"INSERT OR IGNORE INTO chunks(type, data, crc) VALUES(?, ?, ?);", chunk
			)
			cur.execute(
				"INSERT INTO images(id, position, chunk_crc) VALUES(?, ?, ?);",
				(image_id, position, chunk.crc),
			)
		
		self.conn.commit()
		cur.close()

		return image_id

	def get_image(self, f: BufferedIOBase, image_id: int):
		cur = self.conn.cursor()
		png.pack_png(
			f,
			map(
				lambda x: png.Chunk(*x),
				cur.execute(
					"""SELECT chunks.* FROM images
					INNER JOIN chunks ON images.chunk_crc = chunks.crc
					WHERE id = ?
					ORDER BY images.position""",
					[image_id],
				),
			),
		)
		self.conn.commit()
		cur.close()

	def close(self):
		self.conn.close()


if __name__ == "__main__":
	tree = PNGTree()
	with open("album-cover.png", "rb") as f:
		with open("album-cover-again.png", "wb") as f2:
			tree.get_image(f2, tree.insert_image(f))
