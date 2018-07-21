from marshmallow import Schema, fields, validates_schema, ValidationError


class CustomField(fields.Field):
    pass


class StrictSchema(Schema):
    @validates_schema(pass_original=True)
    def check_unknown_fields(self, _, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', list(unknown))


class SubscriptionRequest(StrictSchema):
    token = fields.Str(required=True)
    topic = fields.Str(required=True)


class SubscriptionResponse(Schema):
    result = fields.Bool(required=True, dump_only=True)
    detail = fields.Dict(dump_only=True)


class PublishPayload(Schema):
    topic = fields.Str(required=True, dump_only=True)
    payload = CustomField(required=True, dump_only=True)
