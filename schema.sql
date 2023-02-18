create table video (
  service text not null,
  service_id text not null,
  title text,
  artist text,
  upload_date date,
  description text,
  duration_ms integer,
  filepath text,
  primary key(service, service_id)
);

create table subtitles (
  service text not null,
  service_id text not null,
  isolang3 text,
  subtitles text,
  codec text,
  primary key(service, service_id, isolang3),
  foreign key(service, service_id) references video(service, service_id)
);

create table chapter (
  service text not null,
  service_id text not null,
  chapter_uid integer,
  start_ms integer,
  end_ms integer,
  primary key(service, service_id, chapter_uid),
  foreign key(service, service_id) references video(service, service_id)
);

create table chapterdisplay (
  service text not null,
  service_id text not null,
  chapter_uid integer,
  isolang3 text,
  chapterstring text,
  primary key(service, service_id, chapter_uid, isolang3),
  foreign key(service, service_id) references video(service, service_id)
);
