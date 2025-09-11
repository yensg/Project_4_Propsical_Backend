CREATE TABLE roles (
role VARCHAR(20) PRIMARY KEY
);

INSERT INTO roles(role) VALUES ('admin'), ('registered'), ('subscribed'),('guest');

SELECT * FROM roles;


CREATE TABLE subscription_plans (
subscription_plan VARCHAR(20) PRIMARY KEY,
subscription_plan_cost DECIMAL(7,2) NOT NULL
);

INSERT INTO subscription_plans(subscription_plan,subscription_plan_cost) VALUES ('basic',99.99),('premium',999.99),('enterprise',9999.99);


CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
  registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
  username VARCHAR(120) NOT NULL UNIQUE,
  email VARCHAR(120),
  name TEXT,
  phone TEXT CHECK (phone ~ '^\+[1-9][0-9]{6,14}$'),
  hash TEXT NOT NULL,
  
  role VARCHAR(20) NOT NULL,
  CONSTRAINT fk_role FOREIGN KEY (role) REFERENCES roles(role),          
  
  subscribed_date DATE,
  
  subscription_plan VARCHAR(20) NOT NULL,
  CONSTRAINT fk_subscription_plan FOREIGN KEY (subscription_plan) REFERENCES subscription_plans(subscription_plan) 
);


CREATE TABLE bedrooms (
bedroom INT2 PRIMARY KEY
);

CREATE TABLE toilets (
toilet INT2 PRIMARY KEY
);

CREATE TABLE types (
type VARCHAR(20) PRIMARY KEY
);

INSERT INTO bedrooms VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);
INSERT INTO toilets VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);
INSERT INTO types VALUES ('residential'), ('commercial'), ('retail'), ('industrial');


CREATE TABLE listings (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
asking_price DECIMAL(10,0) NOT NULL,
floor_size INT2 NOT NULL,
land_size INT2,

bedroom INT2 NOT NULL,
CONSTRAINT fk_bedroom FOREIGN KEY (bedroom) REFERENCES bedrooms(bedroom),

toilet INT2 NOT NULL,
CONSTRAINT fk_toilet FOREIGN KEY (toilet) REFERENCES toilets(toilet),

type VARCHAR(20) NOT NULL,
CONSTRAINT fk_type FOREIGN KEY (type) REFERENCES types(type),

unit_number TEXT NOT NULL,
location TEXT NOT NULL,
geo_lat NUMERIC(9,6),
geo_lon NUMERIC(9,6),
summary TEXT,
description TEXT,
account_id UUID,
CONSTRAINT fk_account_id FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE cloudinary (
id SERIAL PRIMARY KEY,
image TEXT NOT NULL,
listing_id UUID,
CONSTRAINT fk_listing_id FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
);

DROP TABLE cloudinary;
DROP TABLE listings;


CREATE TABLE appointments (
uid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
dtstamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
dtstart TIMESTAMPTZ NOT NULL,
dtend TIMESTAMPTZ NOT NULL,
summary TEXT NOT NULL,
description TEXT,
listing_id UUID,
CONSTRAINT fk_appt_listing FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
url TEXT,
status TEXT CHECK (status IN ('TENTATIVE','CONFIRMED','CANCELLED')),

  -- start time must be on :00, :15, :30, :45
  CONSTRAINT chk_start_block
    CHECK (EXTRACT(MINUTE FROM dtstart) IN (0, 30)),

  -- duration must be exactly 30 min or 60 min
  CONSTRAINT chk_duration
    CHECK (
      dtend = dtstart + interval '30 minutes'
      OR dtend = dtstart + interval '1 hour'
    )
);


ALTER TABLE appointments
  ADD COLUMN is_block BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE appointments
  ADD CONSTRAINT chk_start_block
    CHECK (EXTRACT(MINUTE FROM dtstart) IN (0, 30)),
  ADD CONSTRAINT chk_duration
    CHECK (
      dtend = dtstart + interval '30 minutes'
      OR dtend = dtstart + interval '1 hour'
    );
