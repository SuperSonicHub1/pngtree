# PNGTree

an interesting but ultimately fruitless exploration of lossless image compression at scale

```sql
select id, chunk_crc, count(*) as c, chunks.* from images inner join chunks on chunks.crc = images.chunk_crc  group by chunk_crc having c > 1 order by c;
```

| chunk_crc  | count | type | data |    crc     |
|------------|-------|------|------|------------|
| 2065318829 | 4064  | IHDR |      | 2065318829 |
| 2923585666 | 4065  | IEND |      | 2923585666 |

This table represents everything that went wrong with my project:
- the only duplicate chunks are IHDR and IEND
	- IHDR contains the core metadata of a PNG (dimensions, color, etc) and my
	[dataset](https://www.gwern.net/Crops) very intenionally normalizes the resolution
	of images
		- this would hold up still in the real world but not by much
	- every PNG has the same IEND and it's only eight bytes saved anyway

With how little I save due to only havign IHDR and IEND dupes combined with the overhead of SQLite, my `images.sqlite` DB ends up being as large as the raw files it contains.

This is in part due to relying on PNG's chunk system a little too much. No two chunks
are alike, mostly due to PNG's multiple forms of compression. It's likely that if I stored
hundreds of thousands of images in the DB instead of just a couple thousand that we might
find some dupes, but it likely wouldn't be enough to make everything happen.

If I ever return to this project, I'll need to figure out how to normalize PNG chunks.
For now, I'm just going to post this online and perhaps explore more generic approaches.
