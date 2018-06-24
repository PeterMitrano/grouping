-- Create table for samples
drop table if exists samples;
create table samples (
  url text not null primary key,
  count integer not null
);

-- Create table for labelers
drop table if exists labelers;
create table labelers (
  id integer primary key autoincrement,
  labeler_id text not null unique
);

-- Create table for responses
drop table if exists responses;
create table responses (
  id integer primary key autoincrement,
  url text not null,
  ip_addr text not null,
  stamp timestamp not null, -- the number of seconds since 1970-01-01 00:00:00 UTC
  labeler_id integer not null,
  experiment_id text not null,
  metadata text,
  data text not null,
  CONSTRAINT key_labeler FOREIGN KEY (labeler_id) REFERENCES labelers (labeler_id),
  CONSTRAINT key_url FOREIGN KEY (url) REFERENCES samples (url)
);
