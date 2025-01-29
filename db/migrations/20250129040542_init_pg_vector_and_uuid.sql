-- migrate:up

create extension if not exists "uuid-ossp";
create extension if not exists vector;

-- migrate:down

drop extension if exists "uuid-ossp";
drop extension if exists vector; -- not sure if you'd want to do this with
 -- our PG container...
