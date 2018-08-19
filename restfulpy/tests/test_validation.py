from datetime import date, time

import pytest
from nanohttp import HTTPBadRequest, settings, HTTPStatus
from nanohttp.contexts import Context
from sqlalchemy import Integer, Unicode, ForeignKey, Boolean, Table, Date,\
    Time, Float
from sqlalchemy.orm import synonym

from restfulpy.orm import DeclarativeBase, Field, relationship, composite, \
    ModifiedMixin


class Actor(DeclarativeBase):
    __tablename__ = 'actor'

    id = Field(Integer, primary_key=True)
    email = Field(
        Unicode(100),
        not_none='701 email cannot be null',
        required='702 email required',
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        watermark='Email',
        example="user@example.com"
    )
    title = Field(
        Unicode(50),
        index=True,
        min_length=(4, '703 title must be at least 4 characters'),
        max_length=(50, '704 Maximum allowed length for title is 50'),
        watermark='First Name',
    )
    age = Field(
        Integer,
        nullable=True,
        type_checker=(int, '705 age must be integer'),
        minimum=(18, '706 age must be greater than 17'),
        maximum=(99, '706 age must be less than 100')
    )



def test_validation(db):
    session = db()
    email = 'user@example.com'

    validate = Actor.create_validator(strict=True)
    values, querystring = validate(dict(
        email=email,
    ))
    assert values['email'] == email

    # Not None
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=None))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '701 email cannot be null'

    # Required
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(title='required-test-case'))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '702 email required'

    # Minimum length
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=email, title='abc'))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '703 title must be at least 4 characters'

    # Mamimum length
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=email, title='a'*(50+1)))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '704 Maximum allowed length for title is 50'

    # Type
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=email, title='abcd', age='a'))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '705 age must be integer'

    # Minimum
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=email, title='abcd', age=18-1))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '706 age must be greater than 17'

    # Maximum
    with pytest.raises(HTTPStatus) as ctx:
        validate(dict(email=email, title='abcd', age=99+1))
    assert issubclass(ctx.type, HTTPStatus)
    assert isinstance(ctx.value, HTTPStatus)
    assert str(ctx.value) == '706 age must be less than 100'

