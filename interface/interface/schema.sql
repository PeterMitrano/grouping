drop table if exists samples;
create table samples (
  id integer primary key autoincrement,
  url text not null,
  title text not null,
  response_count integer not null
);
