# mkv2sqlite
Converts the metadata in an MKV into a sqlitedb.

To process files in subdirectories, you can use

```sh
find . -iname \*mkv  -print0 | parallel --null --bar './process-file.py videos.sqlite3 {}'
```

sqlite3 will work with multiple processes sharing the same database. `parallel`
will correctly quote the filename passed in via `{}`, so there's no need to
quote it in the command template.

# Generate the yt-dlp download archive

```sh
echo "select service, service_id from video" | sqlite3 -separator ' ' videos.sqlite3 > ytdlarchive
```


# Sample file '20160710 - ALU Design.mkv'

The video was optained via.

```sh
yt-dlp \
  --continue \
  --retries 3 \
  --no-overwrites \
  --write-info-json \
  --write-auto-subs \
  --embed-thumbnail \
  --sub-langs "en,it,es,fr,de" \
  --embed-metadata \
  --embed-chapters \
  --embed-info-json \
  --embed-subs \
  --download-archive "ytdlarchive" \
  --format "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --retry-sleep exp=1::2 \
  --sleep-requests 5 \
  --sleep-interval 30 \
  --sponsorblock-mark all \
  --sponsorblock-chapter-title "[SponsorBlock][%(category)s]: %(name)s" \
  --merge-output-format "mkv" \
  --output "%(channel)s/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=mOVOS9AjgFs"
```

Then `mkvinfo` was used to extract the metadata to view quickly.

```sh
mkvinfo  20160710\ -\ ALU\ Design.mkv > 20160710\ -\ ALU\ Design.mkvinfo
```

However, since I don't feel like writing a parser for that, and Mr. Bunkus
doesn't seem to have any interest what-so-ever in allowing `mkvinfo` to output
json (https://gitlab.com/mbunkus/mkvtoolnix/-/issues/3424), nor does he seem to
have any interest in full output to `mkvmerge`, and has made it quite clear
that he doesn't consider these tools to be "media information tool"
(https://gitlab.com/mbunkus/mkvtoolnix/-/issues/3468). I'm going to intially
try using `mkvextract`, which can only output individual sections of the
metadata on each invocation as XML data, but can't output the file-level
metadata, like the title.

```sh
mkvextract 20160710\ -\ ALU\ Design.mkv chapters 20160710\ -\ ALU\ Design.chapters.xml tags 20160710\ -\ ALU\ Design.tags.xml
mkvmerge --identification-format json --identify 20160710\ -\ ALU\ Design.mkv > 20160710\ -\ ALU\ Design.ident.json
```

# Citations

```
Tange, O. (2022, October 22). GNU Parallel 20221022 ('Nord Stream').
Zenodo. https://doi.org/10.5281/zenodo.7239559
```
