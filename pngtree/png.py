from io import BufferedIOBase
from typing import NamedTuple, Iterator

# CRCs aren't amazing hashes, but good enough for our purposes
# https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Data_integrity

# PNGs are big endian
# https://www.w3.org/TR/PNG/#7Integers-and-byte-order

# struct.pack('>8B', 137, 80, 78, 71, 13, 10, 26, 10)
# https://www.w3.org/TR/PNG/#5PNG-file-signature
PNG_HEADER = b'\x89PNG\r\n\x1a\n'

class Chunk(NamedTuple):
	"""https://www.w3.org/TR/PNG/#5Chunk-layout"""
	type: str
	data: bytes
	crc: int

	def serialize(self) -> bytes:
		return (
			len(self.data).to_bytes(4, 'big')
			+ self.type.encode('ascii')
			+ self.data
			+ self.crc.to_bytes(4, 'big')
		)

ChunkIterator = Iterator[Chunk]

def unpack_png(f: BufferedIOBase) -> ChunkIterator:
	"""https://www.w3.org/TR/PNG/#5DataRep"""
	assert f.readable()

	assert f.read(8) == PNG_HEADER

	iend_reached = False
	while not iend_reached:
		length = int.from_bytes(f.read(4), 'big')
		chunk_type = f.read(4).decode('ascii')
		chunk_data = f.read(length)
		crc = int.from_bytes(f.read(4), 'big')

		iend_reached = chunk_type == 'IEND'

		# Drop non-critical chunks
		# https://www.w3.org/TR/PNG/#table52
		if chunk_type[0].isupper():
			yield Chunk(chunk_type, chunk_data, crc)

def pack_png(f: BufferedIOBase, chunks: ChunkIterator):
	assert f.writable()

	f.write(PNG_HEADER)
	for chunk in chunks: f.write(chunk.serialize())

if __name__ == '__main__':
	with open('album-cover.png', 'rb') as f:
		with open('album-cover-again.png', 'wb') as f2:
			pack_png(f2, unpack_png(f))
