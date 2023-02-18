# mkv2sqlite
Converts the metadata in an MKV into a sqlitedb.


# Sample file '20160710 - ALU Design.mkvinfo'

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

Then `mkvinfo` was used to extract the metadata.

```sh
mkvinfo  20160710\ -\ ALU\ Design.mkv > 20160710\ -\ ALU\ Design.mkvinfo
```
