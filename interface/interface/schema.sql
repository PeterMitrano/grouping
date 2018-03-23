-- Create table for samples
drop table if exists samples;
create table samples (
--  id integer primary key autoincrement,
  url text not null primary key,
  count integer not null
);

-- Create table for responses
drop table if exists responses;
create table responses (
  id integer primary key autoincrement,
  url text not null,
  ip_addr text not null,
  stamp timestamp not null, -- the number of seconds since 1970-01-01 00:00:00 UTC
  experiment_id text not null,
  metadata text not null,
  data text not null
);
