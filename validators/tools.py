from marshmallow import Schema, fields, validate, EXCLUDE

class AddOneToolInputs(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(validate=validate.Length(min=1,  max=50, error='name has to be 1 to 50 characters'), required=True)

    description = fields.Str(validate=validate.Length(min=1, max=150, error='description has to be 1 to 150 characters'), required=True)

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