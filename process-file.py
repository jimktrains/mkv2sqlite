#!/usr/bin/env python3

import subprocess
import argparse
import json
from dataclasses import dataclass
import os
from lxml import etree
import re
import math
import tempfile
import sqlite3

ytidre = re.compile('https://www.youtube.com/watch\?v=(?P<id>[^&]+)')

@dataclass(init=False)
class Video:
  service: str
  service_id: str
  title: str
  artist: str
  upload_date: str
  description: str
  duration_ms: int
  filepath: str

  @staticmethod
  def from_file(filepath):
      v = Video()
      v.filepath = os.path.realpath(filepath)
      return v


  def update_from_identify(self):
    result = subprocess.run(['mkvmerge', '--identification-format', 'json', '--identify', self.filepath], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    ident = json.loads(result.stdout)
    self.title = ident['container']['properties']['title']
    self.duration_ms = ident['container']['properties']['duration']

    return self

  def update_from_tags(self): 
    result = subprocess.run(['mkvextract', self.filepath, 'tags'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    tagroot = etree.fromstring(result.stdout)
    container_tags = tagroot.xpath("//Tag/Targets[count(child::*) = 0]/../Simple")
    container_tags = {''.join(t.xpath('.//Name//text()')): ''.join(t.xpath('.//String//text()')) for t in container_tags}

    self.artist = container_tags.get('ARTIST')
    self.upload_date = container_tags.get('DATE')
    self.description = container_tags.get('DESCRIPTION')
    self.service = None
    self.service_id = None

    if ytid := ytidre.match(container_tags.get('PURL')):
        self.service = 'youtube'
        self.service_id = ytid.group('id')

    return self


@dataclass(init=False)
class Subtitles:
  service: str
  service_id: str
  isolang3: str
  subtitles: str
  codec: str

  @staticmethod  
  def from_video(v):
    result = subprocess.run(['mkvmerge', '--identification-format', 'json', '--identify', v.filepath], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    ident = json.loads(result.stdout)
    subtitle_tracks = [t for t in ident.get('tracks',{}) if t.get('type') == 'subtitles']
    subtitles = []
    with tempfile.TemporaryDirectory() as td:
        for t in subtitle_tracks:
            p = t.get('properties', {})
            s = Subtitles()
            s.service = v.service
            s.service_id = v.service_id
            s.isolang3 = p.get('language')
            s.codec = t.get('codec')

            fn = f"{td}/{t.get('id')}"
            result = subprocess.run(['mkvextract', v.filepath, 'tracks', '--fullraw', f"{t.get('id')}:{fn}"], stdout=subprocess.PIPE)
            if result.returncode != 0:
                print(result)
                exit(result.returncode)
            with open(fn, 'r') as f:
                s.subtitles = f.read()
            subtitles.append(s)
    return subtitles
    

@dataclass(init=False)
class Chapter:
  service: str
  service_id: str
  chapter_uid: int
  start_ms: int
  end_ms: int

  @staticmethod
  def from_video(v):
    result = subprocess.run(['mkvextract', v.filepath, 'chapters'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result)
        exit(result.returncode)
    chapterroot = None
    try:
        chapterroot = etree.fromstring(result.stdout)
    except:
        if len(result.stdout) != 0:
            print(result)
            exit(255)

    chapters = []
    if chapterroot is None:
        return chapters

    for chapter in chapterroot.xpath('//ChapterAtom'):
        c = Chapter()
        c.service = v.service
        c.service_id = v.service_id
        c.chapter_uid = chapter.find('ChapterUID').text

        (h,m,s) = chapter.find('ChapterTimeStart').text.split(':')
        c.start_ms = math.floor(((int(h)*3600) + (int(m)*60) + float(s))*1000)
        (h,m,s) = chapter.find('ChapterTimeEnd').text.split(':')
        c.end_ms = math.floor(((int(h)*3600) + (int(m)*60) + float(s))*1000)

        display = []
        for chapterdisplay in chapter.findall('ChapterDisplay'):
            d = ChapterDisplay()
            d.service = v.service
            d.service_id = v.service_id
            d.chapter_uid = c.chapter_uid
            d.chapterstring = chapterdisplay.find('ChapterString').text
            d.isolang3 = chapterdisplay.find('ChapterLanguage').text
            if d.isolang3 == 'und':
                d.isolang3 = None
            display.append(d)
        chapters.append((c, display))
    return chapters

@dataclass(init=False)
class ChapterDisplay:
  service: str
  service_id: str
  chapter_uid: int
  isolang3: str
  chapterstring: str

parser = argparse.ArgumentParser()
parser.add_argument('dbfilename')
parser.add_argument('videofilename')
args = parser.parse_args()


with sqlite3.connect(args.dbfilename) as con:
    cur = con.cursor()

    v = Video.from_file(args.videofilename)
    res = cur.execute("select 1 from video where filepath = ?", (v.filepath,))
    if len(list(res)) != 0:
        exit(0)

    v = v.update_from_identify().update_from_tags()
    res = cur.execute("select 1 from video where service = ? and service_id = ?", (v.service, v.service_id))
    if len(list(res)) != 0:
        exit(0)

    subtitles = Subtitles.from_video(v)
    chapters = Chapter.from_video(v)
    cur.execute("""insert or ignore into video (
      service,
      service_id,
      title,
      artist,
      upload_date,
      description,
      duration_ms,
      filepath
    ) values (
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?
    )""", (
      v.service,
      v.service_id,
      v.title,
      v.artist,
      v.upload_date,
      v.description,
      v.duration_ms,
      v.filepath
    ));

    for st in subtitles:
        cur.execute("""insert or ignore into subtitles (
          service,
          service_id,
          isolang3,
          subtitles,
          codec
        ) values (
            ?,
            ?,
            ?,
            ?,
            ?
            )
        """, (
          st.service,
          st.service_id,
          st.isolang3,
          st.subtitles,
          st.codec
        ))

    for (c, cds) in chapters:
        cur.execute("""insert or ignore into chapter (
          service,
          service_id,
          chapter_uid,
          start_ms,
          end_ms
        ) values (
            ?,
            ?,
            ?,
            ?,
            ?
        )""", (
          c.service,
          c.service_id,
          c.chapter_uid,
          c.start_ms,
          c.end_ms,
        ))
        for cd in cds:
            cur.execute("""insert or ignore into chapterdisplay (
      service,
      service_id,
      chapter_uid,
      isolang3,
      chapterstring
      ) values (
            ?,
            ?,
            ?,
            ?,
            ?
        )""", (
            cd.service,
            cd.service_id,
            cd.chapter_uid,
            cd.isolang3,
            cd.chapterstring
            ))
