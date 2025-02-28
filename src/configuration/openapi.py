"""OpenAPI 3.1 Object for creating function calls and storing API info in postgres
Docs from https://swagger.io/specification"""

import json
from collections import defaultdict
from contextvars import ContextVar
from typing import Any, Callable, List, Optional, cast
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import (  # type: ignore
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    validator,
    SkipValidation
)
from pydantic.alias_generators import to_camel, to_snake  # type: ignore
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.util import identity_key
from typing_extensions import Self

from common.models import openapi_entity, openapi_server, openapi_path, openapi_operation
from common.session_helper import SessionHelper
from dataclasses import field

# context_session: ContextVar = ContextVar(name="session")

# context_relationships: ContextVar = ContextVar(name="relationships")


config_info: dict = defaultdict(lambda: defaultdict(dict))


class ContactObject(BaseModel):
    """Contact information for the exposed API."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    name: str | None = None
    """The identifying name of the contact person/organization."""

    url: str | None = None
    """The URI for the contact information. This MUST be in the form of a URI."""

    email: str | None = None
    """The email address of the contact person/organization. 
    This MUST be in the form of an email address."""


class LicenseObject(BaseModel):
    """The license information for the exposed API"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    name: str
    """REQUIRED. The license name used for the API."""

    identifier: str | None = None
    """An [SPDX](https://spdx.org/licenses/) license expression for the API. 
    The identifier field is mutually exclusive of the url field."""

    url: str | None = None
    """A URI for the license used for the API. 
    This MUST be in the form of a URI. 
    The url field is mutually exclusive of the identifier field."""


class InfoObject(BaseModel):
    """OpenAPI Info Object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    title: str
    """REQUIRED. The title of the API."""

    version: str
    """REQUIRED. The version of the OpenAPI Document 
    (which is distinct from the OpenAPI Specification version 
    or the version of the API being described or the version 
    of the OpenAPI Description)."""

    summary: str | None = None
    """A short summary of the API."""

    description: str | None = None
    """A description of the API. 
    [CommonMark syntax](https://spec.commonmark.org/) 
    MAY be used for rich text representation."""

    terms_of_service: str | None = None
    """A URI for the Terms of Service for the API. 
    This MUST be in the form of a URI."""

    contact: ContactObject | None = None
    """The contact information for the exposed API."""

    license_: LicenseObject | None = None
    """The license information for the exposed API"""


class ServerVariableObject(BaseModel):
    """An object representing a Server Variable
    for server URL template substitution."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    default: str
    """REQUIRED. The default value to use for substitution, 
    which SHALL be sent if an alternate value is not supplied. 
    If the enum is defined, the value MUST exist in the enum's values. 
    Note that this behavior is different from the Schema Object's default keyword, 
    which documents the receiver's behavior 
    rather than inserting the value into the data."""

    enum: List[str] | None = None
    """An enumeration of string values to be used 
    if the substitution options are from a limited set. 
    The array MUST NOT be empty."""

    description: str | None = None
    """An optional description for the server variable. 
    [CommonMark syntax](https://spec.commonmark.org/) 
    MAY be used for rich text representation."""


class ServerObject(BaseModel):
    """An object representing a Server."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    url: str
    """REQUIRED. A URL to the target host. 
    This URL supports Server Variables and MAY be relative, 
    to indicate that the host location is relative to the location where 
    the document containing the Server Object is being served. 
    Variable substitutions will be made when a variable is named in {braces}."""

    _oas_uuid: UUID | None = None
    _uuid: UUID | None = None

    """The UUID of the containing OpenAPI spec"""
    @model_validator(mode="before")
    def begin(cls, values) -> dict:
        values["_oas_uuid"] = openapi_spec_id.get()
        if values.get("url") is None:
            raise ValueError("field url must not be empty")
        values["_uuid"] = uuid5(namespace=NAMESPACE_URL, name=values["url"])
        return values
    

    
    

    # @validator("_uuid", always=True)
    # @classmethod
    # def validate_uuid(cls, value, values):
    #     return uuid5(namespace=uuid.NAMESPACE_URL, name=values["url"])

    # @validator("_oas_uuid", always=True)
    # @classmethod
    # def validate_oas_uuid(cls, value):
    #     return openapi_spec_id.get()

    description: str | None = None
    """An optional string describing the host designated by the URL. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    variables: dict[str, ServerVariableObject] | None = None
    """A map between a variable name and its value. 
    The value is used for substitution in the server's URL template."""

    # this is done in openapi_parsing.py

    # @model_validator(mode="after")
    # def finish(self) -> Self:
    #     session: scoped_session = config_info[openapi_spec_id.get()]["session"]

    #     db_object = openapi_server.OpenAPIServer(
    #         openapi_server_id=self.uuid, spec_id=self.oas_uuid
    #     )
    #     try:
    #         session.add(db_object)
    #     except IntegrityError:
    #         pass
    #     if session.query(db_object).scalar() is None:
    #         session.add(db_object)
    #     return self


class ExternalDocumentationObject(BaseModel):
    """Allows referencing an external resource for extended documentation"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    url: str
    """REQUIRED. The URI for the target documentation. 
    This MUST be in the form of a URI."""

    description: str | None = None
    """A description of the target documentation.
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""


class ParameterObject(BaseModel):
    """Describes a single operation parameter.

    A unique parameter is defined by a combination of a name and location.

    See [Appendix E](https://swagger.io/specification/#appendix-e-percent-encoding-and-form-media-types)
    for a detailed examination of percent-encoding concerns,
    including interactions with the
    application/x-www-form-urlencoded query string format.

    # Parameter Locations

    There are four possible parameter locations specified by the in field:

        path - Used together with Path Templating, where the parameter value is
            actually part of the operation's URL.
            This does not include the host or base path of the API.
            For example, in /items/{itemId}, the path parameter is itemId.
        query - Parameters that are appended to the URL.
            For example, in /items?id=###, the query parameter is id.
        header - Custom headers that are expected as part of the request.
            Note that RFC7230 states header names are case insensitive.
        cookie - Used to pass a specific cookie value to the API.

    # Fixed Fields

    The rules for serialization of the parameter are specified in one of two ways.
    Parameter Objects MUST include either a content field or a schema field,
    but not both. See Appendix B for a discussion of converting values of
    various types to string representations.

    # Common Fixed Fields
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """These fields MAY be used with either content or schema."""

    name: str
    """REQUIRED. The name of the parameter. Parameter names are case sensitive.

    - If `in` is "path", the name field MUST correspond to 
    a template expression occurring within the path field in the Paths Object. 
    See Path Templating for further information.
    - If `in` is "header" and the name field is "Accept", "Content-Type" or 
    "Authorization", the parameter definition SHALL be ignored.
    - For all other cases, the name corresponds to 
    the parameter name used by the `in` field."""

    in_: str = Field(alias="in")
    """REQUIRED. The location of the parameter. 
    Possible values are "query", "header", "path" or "cookie"."""

    description: str | None = None
    """A brief description of the parameter. 
    This could contain examples of use. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    required: Optional[bool] = False
    """Determines whether this parameter is mandatory. If the parameter location is "path", this field is REQUIRED and its value MUST be True. Otherwise, the field MAY be included and its default value is false."""

    deprecated: Optional[bool] = False

    allow_empty_value: Optional[bool] = False
    """If True, clients MAY pass a zero-length string value in place of 
    parameters that would otherwise be omitted entirely, 
    which the server SHOULD interpret as the parameter being unused. 
    Default value is false. 
    If style is used, and if behavior is n/a (cannot be serialized), 
    the value of allowEmptyValue SHALL be ignored. 
    Interactions between this field and the parameter's Schema Object are 
    implementation-defined. This field is valid only for query parameters. 
    Use of this field is NOT RECOMMENDED, 
    and it is likely to be removed in a later revision."""

    x_cuecode: str | None = Field(default=None, alias="x-cuecode")

    @model_validator(mode="after")
    def finish(self) -> Self:
        session: scoped_session = config_info[openapi_spec_id.get()]["session"]
        noun_prompt = self.x_cuecode
        if noun_prompt is None:
            noun_prompt = self.description
        if self.description is None:
            noun_prompt = self.name
        if (
            session.execute(
                select(openapi_entity.OpenAPIEntity).where(
                    openapi_entity.OpenAPIEntity.noun_prompt == noun_prompt
                )
            ).scalar()
            is None
        ):
            session.add(
                openapi_entity.OpenAPIEntity(
                    openapi_entity_id=uuid4(),
                    contained_in_oa_spec_id=openapi_spec_id.get(),
                    noun_prompt=noun_prompt,
                )
            )
        return self

class ExampleObject(BaseModel):
    """An object grouping an internal or external example value with basic
    summary and description metadata. This object is typically used in fields
    named examples (plural), and is a referenceable alternative to older example
    (singular) fields that do not support referencing or metadata.

    Examples allow demonstration of the usage of properties, parameters and
    objects within OpenAPI."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    summary: str | None = None
    """Short description for the example."""

    description: str | None = None
    """Long description for the example. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    # TODO: parse as plaintext string
    value: object | None = None
    """Embedded literal example. The value field and externalValue field are 
    mutually exclusive. To represent examples of media types that cannot 
    naturally represented in JSON or YAML, use a string value to contain the 
    example, escaping where necessary."""

    external_value: str | None = None
    """A URI that identifies the literal example. 
    This provides the capability to reference examples that cannot easily be 
    included in JSON or YAML documents. The value field and externalValue field 
    are mutually exclusive. See the rules for resolving Relative References."""

class ParameterObjectSchema(ParameterObject):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    style: str

    @model_validator(mode="before")
    def validate_style(cls, values):
        if not "style" in data:
            if values["in"] == "query" or "cookie":
                values["style"] = "form"
            elif values["in"] == "path" or "header":
                values["style"] = "simple"

    explode: bool = False

    allow_reserved: bool = False

    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    """Schema for parameters"""

    example: Any | None = None

    examples: dict[str, ExampleObject] | None = None


class ParameterObjectContent(ParameterObject):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    content: dict[str, "MediaTypeObject"] | None = None


class DiscriminatorObject(BaseModel):
    """When request bodies or response payloads may be one of a number of
    different schemas, a Discriminator Object gives a hint about the expected
    schema of the document. This hint can be used to aid in serialization,
    deserialization, and validation. The Discriminator Object does this by
    implicitly or explicitly associating the possible values of a named property
    with alternative schemas.

    Note that discriminator MUST NOT change the validation outcome of the
    schema."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    propety_name: str
    """REQUIRED. The name of the property in the payload that will hold the 
    discriminating value. This property SHOULD be required in the payload 
    schema, as the behavior when the property is absent is undefined."""

    mapping: dict[str, str] | None = None
    """An object to hold mappings between payload values and schema names or 
    URI references."""


class XMLObject(BaseModel):
    """A metadata object that allows for more fine-tuned XML model definitions.

    When using arrays, XML element names are not inferred
    (for singular/plural forms) and the name field SHOULD be used to add that
    information."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    name: str | None = None
    """Replaces the name of the element/attribute used for the described schema 
    property. When defined within items, it will affect the name of the 
    individual XML elements within the list. When defined alongside type being 
    "array" (outside the items), it will affect the wrapping element if and only 
    if wrapped is True. If wrapped is false, it will be ignored."""

    namespace: str | None = None
    """The URI of the namespace definition. 
    Value MUST be in the form of a non-relative URI."""

    prefix: str | None = None
    """The prefix to be used for the name."""

    attribute: Optional[bool] = False
    """Declares whether the property definition translates to an attribute 
    instead of an element. Default value is false."""

    wrapped: Optional[bool] = False
    """MAY be used only for an array definition. 
    Signifies whether the array is wrapped 
    (for example, <books><book/><book/></books>) or unwrapped (<book/><book/>). 
    Default value is false. 
    The definition takes effect only when defined alongside type being "array" 
    (outside the items)."""


class SchemaObject(BaseModel):
    """https://swagger.io/specification/#schema-object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    discriminator: DiscriminatorObject | None = None
    """Adds support for polymorphism. 
    The discriminator is used to determine which of a set of schemas a payload 
    is expected to satisfy. 
    See [Composition and Inheritance](https://swagger.io/specification/#composition-and-inheritance-polymorphism) 
    for more details."""

    xml: XMLObject | None = None
    """This MAY be used only on property schemas. 
    It has no effect on root schemas. 
    Adds additional metadata to describe the XML representation of this 
    property."""

    external_docs: ExternalDocumentationObject | None = None
    """Additional external documentation for this schema."""

    example: object | None = None
    """A free-form field to include an example of an instance for this schema. 
    To represent examples that cannot be naturally represented in JSON or YAML, 
    a string value can be used to contain the example with escaping 
    where necessary.

    Deprecated: The example field has been deprecated in favor of the 
    JSON Schema examples keyword. Use of example is discouraged, 
    and later versions of this specification may remove it."""


class HeaderObject(BaseModel):
    """Describes a single header for HTTP responses and for individual parts in
    multipart representations; see the relevant Response Object and
    Encoding Object documentation for restrictions on which headers can be
    described.

    The Header Object follows the structure of the Parameter Object,
    including determining its serialization strategy based on whether schema or
    content is present, with the following changes:

    1. `name` MUST NOT be specified, it is given in the corresponding headers
    map.
    2. `in` MUST NOT be specified, it is implicitly in header.
    3. All traits that are affected by the location MUST be applicable to a
    location of header (for example, style). This means that allowEmptyValue and
    allowReserved MUST NOT be used, and style, if used, MUST be limited to
    "simple".

    # Fixed Fields
    ## Common Fixed Fields

    These fields MAY be used with either content or schema."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    description: str | None = None
    """A brief description of the header. This could contain examples of use. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    required: bool = False
    """Determines whether this header is mandatory."""

    deprecated: bool = False
    """Specifies that the header is deprecated and 
    SHOULD be transitioned out of usage."""


class HeaderObjectSchema(HeaderObject):
    style: str | None = "simple"
    """Describes how the header value will be serialized. 
    The default (and only legal value for headers) is "simple"."""

    explode: bool = False
    """When this is true, header values of type array or object generate a 
    single header whose value is a comma-separated list of the array items or 
    key-value pairs of the map, see Style Examples. For other data types this 
    field has no effect. The default value is false."""

    schema_: SchemaObject | None = Field(alias="schema", default=None)

    example: Any

    examples: dict[str, ExampleObject] | None = None


class HeaderObjectContent(HeaderObject):
    content: dict[str, "MediaTypeObject"] | None = None
    """A map containing the representations for the header. 
    The key is the media type and the value describes it. 
    The map MUST only contain one entry."""


class EncodingObject(BaseModel):
    """A single encoding definition applied to a single schema property.
     See Appendix B for a discussion of converting values of various types to
     string representations.

    Properties are correlated with multipart parts using the name parameter of
    Content-Disposition: form-data, and with application/x-www-form-urlencoded
    using the query string parameter names. In both cases, their order is
    implementation-defined.

    See Appendix E for a detailed examination of percent-encoding concerns for
    form media types.
    # Fixed Fields
    ## Common Fixed Fields

    These fields MAY be used either with or without the RFC6570-style
    serialization fields defined in the next section below."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    content_type: str | None = None
    """The Content-Type for encoding a specific property. 
    The value is a comma-separated list, each element of which is either a 
    specific media type (e.g. image/png) or a wildcard media type (e.g. image/*). 
    Default value depends on the property type as shown in the table below."""

    headers: dict[str, HeaderObject] | None = None
    """A map allowing additional information to be provided as headers. 
    Content-Type is described separately and SHALL be ignored in this section. 
    This field SHALL be ignored if the request body media type is not a 
    multipart."""


class MediaTypeObject(BaseModel):
    """Each Media Type Object provides schema and examples for the media type
    identified by its key.

    When example or examples are provided, the example SHOULD match the
    specified schema and be in the correct format as specified by the media
    type and its encoding.
    The example and examples fields are mutually exclusive,
    and if either is present it SHALL override any example in the schema.
    See [Working With Examples](https://swagger.io/specification/#working-with-examples)
    for further guidance regarding the different ways of specifying examples,
    including non-JSON/YAML values."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    # TODO: make this always be parsed as a string
    example: object | None = None
    """Example of the media type"""

    examples: dict[str, ExampleObject] | None = None
    """Examples of the media type"""

    encoding: dict[str, EncodingObject] | None = None
    """A map between a property name and its encoding information. 
    The key, being the property name, MUST exist in the schema as a property. 
    The encoding field SHALL only apply to Request Body Objects, 
    and only when the media type is multipart or 
    application/x-www-form-urlencoded. 
    If no Encoding Object is provided for a property, 
    the behavior is determined by the default values documented for the 
    Encoding Object."""

    schema_: dict[str, Any] | None = Field(alias="schema", default=None)
    """The schema defining the content of the request, 
    response, parameter, or header."""


class RequestBodyObject(BaseModel):
    """Describes a single request body."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    content: dict[str, MediaTypeObject]
    """REQUIRED. The content of the request body. 
    The key is a media type or media type range and the value describes it. 
    For requests that match multiple keys, 
    only the most specific key is applicable. 
    e.g. \"text/plain\" overrides \"text/*\""""

    description: str | None = None
    """A brief description of the request body. 
    This could contain examples of use. 
    CommonMark syntax MAY be used for rich text representation."""

    required: Optional[bool] = False
    """Determines if the request body is required in the request. 
    Defaults to false."""


class LinkObject(BaseModel):
    """The Link Object represents a possible design-time link for a response.
    The presence of a link does not guarantee the caller's ability to
    successfully invoke it, rather it provides a known relationship and
    traversal mechanism between responses and other operations.

    Unlike dynamic links (i.e. links provided in the response payload),
    the OAS linking mechanism does not require link information in the runtime
    response.

    For computing links and providing instructions to execute them,
    a runtime expression is used for accessing values in an operation
    and using them as parameters while invoking the linked operation."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    operation_ref: str | None = None

    operation_id: str | None = None

    # TODO: evaluate constants/expressions
    parameters: dict[str, object] | None = None
    """A map representing parameters to pass to an operation as specified with 
    operationId or identified via operationRef. The key is the parameter name 
    to be used (optionally qualified with the parameter location, 
    e.g. path.id for an id parameter in the path), 
    whereas the value can be a constant or an expression to be evaluated and 
    passed to the linked operation."""

    # TODO: evaluate constants/expressions
    request_body: object | None = None
    """A literal value or {expression} to use as a request body when calling 
    the target operation."""

    description: str | None = None
    """A description of the link.
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    server: ServerObject | None = None


class ResponseObject(BaseModel):
    """Describes a single response from an API operation,
    including design-time, static links to operations based on the response."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    description: str
    """REQUIRED. A description of the response. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    headers: dict[str, HeaderObject] | None = None
    """Maps a header name to its definition. 
    RFC7230 states header names are case insensitive. 
    If a response header is defined with the name "Content-Type", 
    it SHALL be ignored."""

    content: dict[str, MediaTypeObject] | None = None
    """A map containing descriptions of potential response payloads. 
    The key is a media type or media type range and the value describes it. 
    For responses that match multiple keys, only the most specific key is 
    applicable. e.g. \"text/plain\" overrides \"text/*\""""

    links: dict[str, LinkObject] | None = None
    """A map of operations links that can be followed from the response. 
    The key of the map is a short name for the link, 
    following the naming constraints of the names for Component Objects."""


SecurityRequirementObjects = List[dict[str, List[str]]]


class OperationObject(BaseModel):
    """Describes a single API operation on a path."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    tags: List[str] | None = None
    """A list of tags for API documentation control. 
    Tags can be used for logical grouping of operations 
    by resources or any other qualifier."""

    summary: str | None = None
    """A short summary of what the operation does."""

    description: str | None = None
    """
    A verbose explanation of the operation behavior. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation.
    """

    external_docs: ExternalDocumentationObject | None = None
    """Additional external documentation for this operation."""

    operation_id: str | None = None
    """Unique string used to identify the operation. 
    The id MUST be unique among all operations described in the API. 
    The operationId value is case-sensitive. 
    Tools and libraries MAY use the operationId to uniquely identify an 
    operation, therefore, it is RECOMMENDED to follow 
    common programming naming conventions."""

    parameters: List[ParameterObject] | None = None
    """A list of parameters that are applicable for this operation. 
    If a parameter is already defined at the Path Item, the new definition will 
    override it but can never remove it. 
    The list MUST NOT include duplicated parameters. 
    A unique parameter is defined by a combination of a name and location. 
    The list can use the Reference Object to link to parameters that are 
    defined in the OpenAPI Object's components.parameters."""

    request_body: RequestBodyObject | None = None
    """The request body applicable for this operation. 
    The requestBody is fully supported in HTTP methods where the HTTP 1.1 
    specification RFC7231 has explicitly defined semantics for request bodies. 
    In other cases where the HTTP spec is vague (such as GET, HEAD and DELETE), 
    requestBody is permitted but does not have well-defined semantics and 
    SHOULD be avoided if possible."""

    responses: dict[str, ResponseObject] | None = None
    """The list of possible responses as they are returned from executing this 
    operation."""

    callbacks: dict[str, dict[object, "PathItemObject"]] | None = None
    """A map of possible out-of band callbacks related to the parent operation. 
    The key is a unique identifier for the Callback Object. 
    Each value in the map is a Callback Object that describes a request that 
    may be initiated by the API provider and the expected responses."""

    security: SecurityRequirementObjects | None = None
    """Each name MUST correspond to a security scheme which is declared in the 
    Security Schemes under the Components Object. 
    If the security scheme is of type "oauth2" or "openIdConnect", 
    then the value is a list of scope names required for the execution, 
    and the list MAY be empty if authorization does not require a specified 
    scope. For other security scheme types, the array MAY contain a list of 
    role names which are required for the execution, but are not otherwise 
    defined or exchanged in-band."""

    servers: List[ServerObject] | None = None
    """An alternative servers array to service this operation. 
    If a servers array is specified at the Path Item Object or OpenAPI Object 
    level, it will be overridden by this value."""

    deprecated: bool | None = None
    """Declares this operation to be deprecated. Consumers SHOULD refrain from 
    usage of the declared operation."""

    x_cuecode: str | None = Field(alias="x-cuecode", default=None)


class PathItemObject(BaseModel):
    """Describes the operations available on a single path.
    A Path Item MAY be empty, due to
    [ACL constraints](https://swagger.io/specification/#security-filtering).
    The path itself is still exposed to the documentation viewer
    but they will not know which operations and parameters are available."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake, serialization_alias=to_camel
        ),
        populate_by_name=True,
        extra="allow",
    )
    """This object MAY be extended with Specification Extensions."""

    summary: str | None = None
    """An optional string summary, 
    intended to apply to all operations in this path."""

    description: str | None = None
    """An optional string description, 
    intended to apply to all operations in this path. 
    [CommonMark syntax](https://spec.commonmark.org/)
    MAY be used for rich text representation."""

    get: OperationObject | None = None
    """A definition of a GET operation on this path."""

    put: OperationObject | None = None
    """A definition of a PUT operation on this path."""

    post: OperationObject | None = None
    """A definition of a POST operation on this path."""

    delete: OperationObject | None = None
    """A definition of a DELETE operation on this path."""

    options: OperationObject | None = None
    """A definition of a OPTIONS operation on this path."""

    head: OperationObject | None = None
    """A definition of a HEAD operation on this path."""

    patch: OperationObject | None = None
    """A definition of a PATCH operation on this path."""

    trace: OperationObject | None = None
    """A definition of a TRACE operation on this path."""

    servers: List[ServerObject] | None = None
    """An alternative servers array to service all operations in this path. 
    If a servers array is specified at the OpenAPI Object level, 
    it will be overridden by this value."""

    parameters: List[ParameterObject] | None = None
    """A list of parameters that are applicable for all the operations 
    described under this path. These parameters can be overridden at the 
    operation level, but cannot be removed there. The list MUST NOT include 
    duplicated parameters. A unique parameter is defined by a combination of a 
    name and location. The list can use the Reference Object to link to 
    parameters that are defined in the OpenAPI Object's 
    components.parameters."""

    ref_: str | None = Field(alias="$ref", default=None)
    """Allows for a referenced definition of this path item. 
    The value MUST be in the form of a URI, 
    and the referenced structure MUST be in the form of a Path Item Object. 
    In case a Path Item Object field appears both in the defined object 
    and the referenced object, the behavior is undefined. 
    See the rules for resolving 
    [Relative References](https://swagger.io/specification/#relative-references-in-api-description-uris)."""

    x_cuecode: str | None = Field(alias="x-cuecode", default=None)

    @model_validator(mode='after')
    def finish(self) -> Self:

        return self

    


context_tag_uuids: ContextVar[dict] = ContextVar("tag_uuids")
context_tags: ContextVar[dict] = ContextVar("tags")


class TagObject(BaseModel):
    """Tag Object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake, serialization_alias=to_camel
        ),
        populate_by_name=True,
        extra="allow",
    )
    name: str
    """REQUIRED. The name of the tag."""

    description: str | None = None
    """A description for the tag. 
    CommonMark syntax MAY be used for rich text representation."""

    x_cuecode: str | None = Field(default=None, alias="x-cuecode")

    externalDocs: ExternalDocumentationObject | None = None

    openapi_entity_id: UUID = Field(default_factory=lambda: uuid4())

    @model_validator(mode="after")
    def finish(self) -> Self:

        # tag_noun_prompt=self.x_cuecode
        # if tag_noun_prompt is None:
        #     tag_noun_prompt = self.description
        # if tag_noun_prompt is None:
        #     tag_noun_prompt = self.name

        # session: scoped_session = context_session.get()
        # entity = openapi_entity.OpenAPIEntity(
        #     openapi_entity_id = self.openapi_entity_id,
        #     contained_in_oa_spec_id = openapi_spec_id.get(),
        #     noun_prompt=tag_noun_prompt
        # )
        # if session.execute(
        #     select(openapi_entity.OpenAPIEntity)
        #         .where(openapi_entity.OpenAPIEntity.noun_prompt == tag_noun_prompt)
        # ).scalar() is None:
        #     session.add(entity)
        #     tag_map: dict = context_tag_uuids.get()
        #     tag_map[self.name] = self.openapi_entity_id
        #     context_tag_uuids.set(tag_map)

        return self


class OAuthFlowObject(BaseModel):
    """Individual OAuth Flow Object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    authorization_url: str | None
    """only applies to oauth2 (\"implicit\", \"authorizationCode\") 
    REQUIRED. The authorization URL to be used for this flow. 
    This MUST be in the form of a URL. 
    The OAuth2 standard requires the use of TLS."""

    token_url: str | None = None
    """only applies to oauth2(\"password\", 
    \"clientCredentials\", \"authorizationCode\"). REQUIRED.
    The token URL to be used for this flow. This MUST be in the form of a URL. 
    The OAuth2 standard requires the use of TLS."""

    refresh_url: str | None = None
    """The URL to be used for obtaining refresh tokens. 
    This MUST be in the form of a URL. 
    The OAuth2 standard requires the use of TLS."""

    scopes: dict[str, str] = {}
    """REQUIRED. The available scopes for the OAuth2 security scheme. 
    A map between the scope name and a short description for it. 
    The map MAY be empty."""


class OAuthFlowsObject(BaseModel):
    """OAsuth Flows object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    implicit: OAuthFlowObject | None = None
    password: OAuthFlowObject | None = None
    client_credentials: OAuthFlowObject | None = None
    authorization_code: OAuthFlowObject | None = None


class SecuritySchemeObject(BaseModel):
    """Security Scheme Object"""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    type: str
    """REQUIRED: type of security scheme; Valid values are 'apiKey', 'http', 
    'mutualTLS', 'oath2', 'openIdConnect'."""

    description: str | None = None

    name: str | None = None
    """only applies to apiKey. REQUIRED. 
    The name of the header, query or cookie parameter to be used."""

    in_: str | None = Field(alias="in", default=None)
    """only applies to apiKey. REQUIRED. The location of the API key. 
    Valid values are \"query\", \"header\" or \"cookie\"."""

    scheme: str | None = None
    """only applies to http. REQUIRED. 
    The name of the HTTP Authorization scheme to be used in the 
    Authorization header as defined in [RFC7235] Section 5.1. 
    The values used SHOULD be registered in the IANA Authentication Scheme 
    registry."""

    bearer_format: str | None = None
    """only applies to http ("bearer). A hint to the client to identify how the 
    bearer token is formatted. Bearer tokens are usually generated by an 
    authorization server, so this information is primarily for documentation 
    purposes."""

    flows: OAuthFlowsObject | None = None
    """only applies to oauth2. REQUIRED. An object containing configuration
    information for the flow types supported"""

    open_id_connect_url: str | None = None
    """only applies to openIdConnect. REQUIRED. 
    OpenId Connect URL to discover OAuth2 configuration values. 
    This MUST be in the form of a URL. 
    The OpenID Connect standard requires the use of TLS."""


class ComponentsObject(BaseModel):
    """Components Object Removing this might be beneficial,
    since references are already resolved. Testing needed."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
        extra="allow",
    )

    schemas: dict[str, SchemaObject] | None = None
    responses: dict[str, ResponseObject] | None = None
    parameters: dict[str, ParameterObject] | None = None
    examples: dict[str, ExampleObject] | None = None
    request_bodies: dict[str, RequestBodyObject] | None = None
    headers: dict[str, HeaderObject] | None = None
    security_schemes: dict[str, SecuritySchemeObject] | None = None


openapi_spec_id: ContextVar = ContextVar("openapi_spec_id")
"""generate a new OpenAPI Spec UUID for storing in the database"""


class OpenAPIObject(BaseModel):
    """Deserialized OpenAPI 3.1 Specification"""

    openapi_spec_uuid: UUID | None = None

    db_session: scoped_session | None = None

    base_url: str | None = None

    session_errors_encountered: bool = False
  
        

    @model_validator(mode='before')
    @classmethod
    def validate_model(cls, values):
        try:
            spec_id = values["openapi_spec_uuid"]
        except KeyError:
            raise ValueError(
                "openapi_spec_uuid must be passed as the second positional keyword"
            )

        try:
            session = values["db_session"]
        except KeyError:
            raise ValueError(
                "db_session must be passed as the second positional keyword"
            )

        try:
            base_url = values["base_url"]
        except KeyError:
            raise ValueError("base_url must be passed as the third positional keyword")

        


        id_token = openapi_spec_id.set(spec_id)
        config_info[spec_id]["session"] = session
        return values
        

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_snake, serialization_alias=to_camel
        ),
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True

    )
    """This object MAY be extended with Specification Extensions."""

    openapi: str
    """REQUIRED. This string MUST be the version number of the OpenAPI
    Specification that the OpenAPI Document uses.
    The openapi field SHOULD be used by tooling to interpret the
    OpenAPI Document. This is not related to the API info.version string."""

    info: InfoObject
    """REQUIRED. Provides metadata about the API.
    The metadata MAY be used by tooling as required."""

    paths: dict[str, PathItemObject]
    """The available paths and operations for the API."""

    json_schema_dialect: str | None = None
    """The default value for the $schema keyword within Schema Objects 
    contained within this OAS document. This MUST be in the form of a URI."""

    webhooks: dict[str, PathItemObject] | None = None

    security: SecurityRequirementObjects | None = None

    servers: List[ServerObject] | None = None
    """An array of Server Objects, 
    which provide connectivity information to a target server. 
    If the servers field is not provided, or is an empty array, 
    the default value would be a Server Object with a url value of `/`."""

    tags: List[TagObject] | None = None

    components: ComponentsObject | None = None

    

    @model_validator(mode='after')
    def finish(self) -> Self:
        if self.base_url is None:
            raise ValueError("_base_url missing")
        if self.openapi_spec_uuid is None:
            raise ValueError("_openapi_spec_uuid missing")
        if self.servers is None or not self.servers:
            self.servers = [
                ServerObject(
                    url = self.base_url,
                    description=None,
                    variables=None,
                    _oas_uuid=self.openapi_spec_uuid,
                )
            ]

        for server in self.servers:
            SessionHelper.session_add(
                openapi_server.OpenAPIServer(
                    openapi_server_id=server._uuid,
                    spec_id = self.openapi_spec_uuid, 
                    url=server.url
                ), 
                self.db_session
            )

        for pathname, path in self.paths.items():
            path_id: UUID = uuid4()
            model = openapi_path.OpenAPIPath(
                openapi_path_id = path_id,
                spec_id=self.openapi_spec_uuid, 
                path_templated=pathname
            ), 
            SessionHelper.session_add(
                model,
                self.db_session
            )
            for http_verb in openapi_operation.HttpVerb:
                operation: OperationObject = getattr(path, http_verb.lower())
                if operation is None:
                    continue
                
                servers = operation.servers
                if servers is None:
                    servers = path.servers
                if servers is None:
                    servers = self.servers

                operation_prompt = operation.x_cuecode
                if operation_prompt is None:
                    operation_prompt = operation.description
                if operation_prompt is None:
                    operation_prompt = operation.summary
                if operation_prompt is None:
                    operation_prompt = operation.operation_id
                if operation_prompt is None:
                    operation_prompt = f"pathname:{http_verb}"

                model = openapi_operation.OpenAPIOperation(
                    oa_server_id = servers[0]._uuid,
                    oa_path_id = path_id,
                    http_verb = http_verb.upper(),
                    selection_prompt = operation_prompt,
                    llm_content_gen_tool_cal_spec = self._gen_func(
                        servers=self.servers,
                        path=pathname,
                        operation=operation,
                        operation_name=http_verb
                    )
                )

        return self


    @staticmethod
    def from_formatted_json(spec_id: UUID, db_session: scoped_session, base_url: str, data: dict):
        """create openapi object from json"""
        return OpenAPIObject(openapi_spec_uuid=spec_id, db_session=db_session, base_url=base_url, **data)

    def session_commit(self) -> None:
        if self.db_session is not None:
            self.db_session.commit()

    # TODO: Review & test this, high priority
    @staticmethod
    def _gen_func(
        servers: List[ServerObject],
        path: str,
        operation: OperationObject,
        operation_name: str,
    ) -> dict:
        if operation.servers is not None:
            servers = operation.servers

        func_name = path + "+" + operation_name
        func_description = operation.x_cuecode
        if func_description is None:
            func_description = operation.description
        if func_description is None:
            func_description = operation.summary

        params: dict = {}
        required = []
        if operation.parameters is not None:
            for param in operation.parameters:

                if not isinstance(param, ParameterObjectSchema):
                    continue

                param_description = param.x_cuecode
                if param.description is None:
                    param_description = param.description
                param_info: dict = {}
                if param.schema_ is not None:
                    param_info = param.schema_

                if param_description is not None:
                    param_info["description"] = param_description
                if param.examples is not None:
                    param_info["examples"] = param.examples

                param_name = param.in_ + "/" + param.name
                params[param_name] = param_info

                if param.required:
                    required.append(param_name)

        if operation.request_body is not None:
            request_body_required = False
            if operation.request_body.required:
                request_body_required = True
                required.append("requestBody")

            one_of: dict = {}

            for k, v in operation.request_body.content.items():
                param_info = {}
                if v.schema_ is not None:
                    param_info = v.schema_

                one_of[k] = param_info

            request_body: dict = {"requestBody": {"type": "object", "oneOf": one_of}}

        out: dict = {}

        if len(servers) > 1:
            raise ValueError("Per CueCode restrictions, each unique path must have one and only one server")

        for server in servers:
            
            out[(cast(UUID, server._uuid).int, server.url + path)] = {
                "type": "function",
                "function": {
                    "name": server.url + func_name,
                    "description": func_description,
                    "parameters": {
                        "type": "object",
                        "properties": {**params, **request_body},
                    },
                    "required": required,
                },
            }

        

        return out

    def generate_tools(self) -> dict[int, list]:
        """generate function calls for the api"""

        out: List[dict] = []

        out2: defaultdict = defaultdict(list)
        if self.servers is None:
            raise ValueError("servers cannot be None")

        server_stack = [self.servers]

        for path, path_item in self.paths.items():
            if path_item.servers is not None:
                server_stack.append(path_item.servers)
            if path_item.get is not None:
                result = self._gen_func(server_stack[-1], path, path_item.get, "get")
                for k, v in result.items():
                    out2[k].append(v)
            if path_item.post is not None:
                result = self._gen_func(server_stack[-1], path, path_item.post, "post")
                for k, v in result.items():
                    out2[k].append(v)
            if path_item.head is not None:
                result = self._gen_func(server_stack[-1], path, path_item.head, "head")
                for k, v in result.items():
                    out2[k].append(v)
            if path_item.put is not None:
                result = self._gen_func(server_stack[-1], path, path_item.put, "put")
                for k, v in result.items():
                    out2[k].append(v)
            if path_item.patch is not None:
                result = self._gen_func(
                    server_stack[-1], path, path_item.patch, "patch"
                )
                for k, v in result.items():
                    out2[k].append(v)
            if path_item.trace is not None:
                result = self._gen_func(
                    server_stack[-1], path, path_item.trace, "trace"
                )
                for k, v in result.items():
                    out2[k].append(v)
        return out2
