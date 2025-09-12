from marshmallow import Schema, fields, validate, EXCLUDE

class ValidateRegistration(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(validate=validate.Length(min=1,  max=50, error='username has to be 1 to 50 characters'),allow_none=False, required=True)

    password = fields.Str(validate=validate.Length(min=1, max=150, error='password has to be 1 to 150 characters'),allow_none=False, required=True)

    role = fields.Str(
        required=True, allow_none=False,
        validate=validate.OneOf(['admin','registered','subscribed','guest'],
                       error='role must be one of: admin, registered, subscribed, guest')
    )

    subscription_plan = fields.Str(
        required=True, allow_none=False,
        validate=validate.OneOf(['basic','premium','enterprise'],
                       error='subscription_plan must be one of: basic, premium, enterprise')
    )

    # by default it will return "Missing data for required field." if missing validator?

    name = fields.Str(required=False, allow_none=True, load_default=None)
    email = fields.Email(required=False, allow_none=True, load_default=None)

class ValidateCreateListing(Schema):
    class Meta:
        unknown = EXCLUDE

    asking_price = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=1, max=1000000000, error='asking price must be greater than 0'),
    )

    floor_size = fields.Int(
        required=True,
        validate=validate.Range(min=1,max=50000, error='floor size must be greater than 0'),
    )

    # land_size = fields.Int(
    #     required=False,
    #     allow_none=True,
    #     validate=validate.Range(min=0, error='land size must be 0 or greater')
    # )

    bedroom = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=10, error='bedroom must be between 1 and 10'),
    )

    toilet = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=10, error='toilet must be between 1 and 10'),
    )

    type = fields.Str(
        validate=validate.OneOf(
            ['residential', 'commercial', 'retail', 'industrial'],
            error="type must be one of: residential, commercial, retail, industrial"
        ),
        required=True,
    )

    tenure = fields.Str(
        validate=validate.OneOf(
            [
                "freehold",
                "99-year leasehold",
                "103-year leasehold",
                "110-year leasehold",
                "999-year leasehold",
                "9999-year leasehold",
            ],
            error=(
                "tenure must be one of: freehold, 99-year leasehold, "
                "103-year leasehold, 110-year leasehold, 999-year leasehold, 9999-year leasehold"
            ),
        ),
        required=True,
    )

    unit_number = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20, error="unit number is required")
    )

    location = fields.Str(validate=validate.Length(min=1, max=200, error='location/address is required'), required=True)

    geo_lat = fields.Decimal(
        required=False,
        as_string=True,
        allow_none=True,
        places=6
    )

    geo_lon = fields.Decimal(
        required=False,
        as_string=True,
        allow_none=True,
        places=6
    )

    summary = fields.Str(
        required=False,
        allow_none=True
    )

    account_id = fields.UUID(
        required=False,
        allow_none=True
    )

class Validate_find_all_listings_by_username(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(validate=validate.Length(min=1,  max=50, error='username has to be 1 to 50 characters'),allow_none=False, required=True)

class Validate_UUID_id(Schema):
    class Meta:
        unknown = EXCLUDE

    listing_id = fields.Str(required=True, allow_none=False)