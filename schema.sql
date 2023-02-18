create table video (
  video_id integer primary key autoincrement,
  service text not null,
  service_id text not null,
  title text,
  artist text,
  upload_date date,
  description text,
  duration_sec integer,
  unique(service, service_id),
);

create table subtitles (
  video_id integer,
  isolang3 text,
  subtitles text,
  codec text,
  primary key(video_id, isolang2),
  foreign key(video) references video(video_id)
);

create table chapter (
  video_id integer,
  chapter_uid integer,
  start_sec integer,
  end_sec integer,
  primary key(video_id, chapter_uid),
  foreign key(video) references video(video_id)
);

create table chapterdisplay (
  video_id integer,
  chapter_uid integer,
  isolang3 text,
  chapterstring text,
  primary key(video_id, chapter_uid, lang),
  foreign key(video) references video(video_id)
);
