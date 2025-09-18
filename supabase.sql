create extension if not exists "uuid-ossp";

-- roles table
CREATE TABLE roles (
role VARCHAR(20) PRIMARY KEY
);
INSERT INTO roles(role) VALUES ('admin'), ('registered'), ('subscribed'),('guest');

-- subscription_plans table
CREATE TABLE subscription_plans (
subscription_plan VARCHAR(20) PRIMARY KEY,
subscription_plan_cost DECIMAL(7,2) NOT NULL
);
INSERT INTO subscription_plans(subscription_plan,subscription_plan_cost) VALUES ('basic',99.99),('premium',999.99),('enterprise',9999.99);

-- acocunts table
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
  registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
  username VARCHAR(120) NOT NULL UNIQUE,
  email VARCHAR(120),
  name TEXT,
  phone TEXT CHECK (phone ~ '^\+[1-9][0-9]{6,14}$'),
  hash TEXT NOT NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  
  role VARCHAR(20) NOT NULL,
  CONSTRAINT fk_role FOREIGN KEY (role) REFERENCES roles(role),          
  
  subscribed_date DATE,
  
  subscription_plan VARCHAR(20) NOT NULL,
  CONSTRAINT fk_subscription_plan FOREIGN KEY (subscription_plan) REFERENCES subscription_plans(subscription_plan) 
);
ALTER TABLE accounts DROP CONSTRAINT accounts_phone_check;

-- bedrooms table
CREATE TABLE bedrooms (
bedroom INT2 PRIMARY KEY
);
INSERT INTO bedrooms VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- toilets table
CREATE TABLE toilets (
toilet INT2 PRIMARY KEY
);
INSERT INTO toilets VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- types table
CREATE TABLE types (
type VARCHAR(20) PRIMARY KEY
);
INSERT INTO types VALUES ('residential'), ('commercial'), ('retail'), ('industrial');

-- tenure tables
CREATE TABLE tenures (
tenure VARCHAR(50) PRIMARY KEY
);
INSERT INTO tenures VALUES ('freehold'), ('99-year leasehold'), ('103-year leasehold'), ('110-year leasehold'), ('999-year leasehold'), ('9999-year leasehold');

-- listings table
CREATE TABLE listings (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
asking_price DECIMAL(10,0) NOT NULL,
floor_size INT4 NOT NULL,
land_size INT4,

bedroom INT2 NOT NULL,
CONSTRAINT fk_bedroom FOREIGN KEY (bedroom) REFERENCES bedrooms(bedroom),

toilet INT2 NOT NULL,
CONSTRAINT fk_toilet FOREIGN KEY (toilet) REFERENCES toilets(toilet),

type VARCHAR(20) NOT NULL,
CONSTRAINT fk_type FOREIGN KEY (type) REFERENCES types(type),

tenure VARCHAR(50) NOT NULL,
CONSTRAINT fk_tenure FOREIGN KEY (tenure) REFERENCES tenures(tenure),

unit_number TEXT NOT NULL,
location TEXT NOT NULL,
geo_lat NUMERIC(9,6),
geo_lon NUMERIC(9,6),
summary TEXT,
description TEXT,

account_id UUID,
CONSTRAINT fk_account_id FOREIGN KEY (account_id) REFERENCES accounts(id),

is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE listings
ADD COLUMN tenure VARCHAR(50);
ALTER TABLE listings
ADD CONSTRAINT fk_tenure
FOREIGN KEY (tenure) REFERENCES tenures(tenure);

-- cloudinary table
CREATE TABLE cloudinary (
id SERIAL PRIMARY KEY,
image TEXT NOT NULL,
public_id TEXT NOT NULL,
listing_id UUID,
CONSTRAINT fk_listing_id FOREIGN KEY (listing_id) REFERENCES listings(id),--ON DELETE CASCADE, ON DELETE SET but we seldom use both we should do a flag.
is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- appointments table
CREATE TABLE appointments (
uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
dtstamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
dtstart TIMESTAMPTZ NOT NULL,
dtend TIMESTAMPTZ NOT NULL,
timeslot_is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
date_is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
summary TEXT NOT NULL,
description TEXT,

listing_id UUID,
CONSTRAINT fk_appt_listing FOREIGN KEY (listing_id) REFERENCES listings(id),

url TEXT,
status TEXT CHECK (status IN ('TENTATIVE','CONFIRMED','CANCELLED')),
timeZone TEXT DEFAULT ('Asia/Singapore'),
account_id UUID);

ALTER TABLE appointments
ALTER COLUMN account_id DROP NOT NULL;
ALTER TABLE appointments
  ADD COLUMN account_id UUID;


-- for future use
ALTER TABLE appointments ADD CONSTRAINT chk_duration
CHECK (dtend = dtstart + interval '15 minutes'),

INSERT INTO appointments (
  dtstart, dtend, is_block, summary, description, listing_id, status
)
VALUES (
  '2025-06-12 10:00:00+08',
  '2025-06-12 10:15:00+08',
  FALSE,
  'Viewing',
  'Booked via web UI',
  'f3a5f8b2-4c1e-4a1c-9b0f-12ab34cd56ef', -- example listing_id
  'CONFIRMED'
)
RETURNING *;

-- start time must be on :00, :15, :30, :45
CONSTRAINT chk_start_block
CHECK (EXTRACT(MINUTE FROM dtstart) IN (0, 30));

-- duration must be exactly 30 min or 60 min
ALTER TABLE appointments DROP CONSTRAINT chk_duration;

ALTER TABLE appointments ADD CONSTRAINT chk_duration
CHECK (
  dtend = dtstart + interval '15 minutes'
  OR dtend = dtstart + interval '30 minutes'
  OR dtend = dtstart + interval '1 hour'
);


SELECT * FROM accounts;
SELECT * FROM listings;