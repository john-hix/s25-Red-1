"""Test parsing pet-store-31.json"""
from uuid import UUID, uuid4
from pytest import fixture

import jsonref

from configuration.openapi import OpenAPIObject, ServerObject, PathItemObject, OperationObject, RequestBodyObject, MediaTypeObject, ResponseObject, ParameterObject, HeaderObject
from configuration import config_algo
from pathlib import Path
from configuration.openapi_schema_adapter import OpenAPISchemaAdapter

@fixture
def spec_id() -> UUID:
    return uuid4()

@fixture
def openapi_object(spec_id) -> OpenAPIObject:
    input_file = Path(__file__).parent.parent / "fixtures" / "openapi" / "pet-store-31.json"
    with input_file.open() as file:
        openapi_spec = jsonref.loads(file.read())

        

        formatted_openapi_spec = OpenAPISchemaAdapter._fix_empty_schemas(openapi_spec)
        formatted_openapi_spec = OpenAPISchemaAdapter._fix_broken_security(openapi_spec)
        
        return OpenAPIObject.from_formatted_json(
            spec_id,
            "https://petstore3.swagger.io/",
            formatted_openapi_spec,
            True,
        )

@fixture
def paths(spec_id) -> dict[str, PathItemObject]:
    category_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
                "examples": [
                    1
                ]
            },
            "name": {
                "type": "string",
                "examples": [
                    "Dogs"
                ]
            }
        },
        "xml": {
            "name": "category"
        }
    }
    tag_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "name": {
                "type": "string"
            }
        },
        "xml": {
            "name": "tag"
        }
    }
    pet_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
                "examples": [
                    10
                ]
            },
            "name": {
                "type": "string",
                "examples": [
                    "doggie"
                ]
            },
            "category": category_schema,
            "photoUrls": {
                "type": "array",
                "items": {
                    "type": "string",
                    "xml": {
                        "name": "photoUrl"
                    }
                },
                "xml": {
                    "wrapped": True
                }
            },
            "tags": {
                "type": "array",
                "items": tag_schema,
                "xml": {
                    "wrapped": True
                }
            },
            "status": {
                "description": "pet status in the store",
                "type": "string",
                "enum": [
                    "available",
                    "pending",
                    "sold"
                ]
            }
        },
        "required": [
            "name",
            "photoUrls"
        ],
        "xml": {
            "name": "pet"
        }
    }
    api_response_schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "integer",
                "format": "int32"
            },
            "type": {
                "type": "string"
            },
            "message": {
                "type": "string"
            }
        },
        "xml": {
            "name": "##default"
        }
    }
    order_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
                "examples": [
                    10
                ]
            },
            "petId": {
                "type": "integer",
                "format": "int64",
                "examples": [
                    198772
                ]
            },
            "quantity": {
                "type": "integer",
                "format": "int32",
                "examples": [
                    7
                ]
            },
            "shipDate": {
                "type": "string",
                "format": "date-time"
            },
            "status": {
                "description": "Order Status",
                "type": "string",
                "examples": [
                    "approved"
                ],
                "enum": [
                    "placed",
                    "approved",
                    "delivered"
                ]
            },
            "complete": {
                "type": "boolean"
            }
        },
        "xml": {
            "name": "order"
        }
    }
    user_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
                "examples": [
                    10
                ]
            },
            "username": {
                "type": "string",
                "examples": [
                    "theUser"
                ]
            },
            "firstName": {
                "type": "string",
                "examples": [
                    "John"
                ]
            },
            "lastName": {
                "type": "string",
                "examples": [
                    "James"
                ]
            },
            "email": {
                "type": "string",
                "examples": [
                    "john@email.com"
                ]
            },
            "password": {
                "type": "string",
                "examples": [
                    "12345"
                ]
            },
            "phone": {
                "type": "string",
                "examples": [
                    "12345"
                ]
            },
            "userStatus": {
                "description": "User Status",
                "type": "integer",
                "format": "int32",
                "examples": [
                    1
                ]
            }
        },
        "xml": {
            "name": "user"
        }
    }
    common_security=[
        {
            "petstore_auth": [
                "write:pets",
                "read:pets"
            ]
        }
    ]

    return {
        "/pet": PathItemObject(
            put=OperationObject(
                operation_id="updatePet",
                summary="Update an existing pet",
                description="Update an existing pet by Id",
                request_body=RequestBodyObject(
                    required=True,
                    description="Update an existent pet in the store",
                    content={
                        "application/json": MediaTypeObject(schema_=pet_schema),
                        "application/x-www-form-urlencoded": MediaTypeObject(schema_=pet_schema),
                        "application/xml": MediaTypeObject(schema_=pet_schema)
                    }
                ),
                responses={
                    "200": ResponseObject(
                        description="Successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=pet_schema),
                            "application/xml": MediaTypeObject(schema_=pet_schema),
                        }
                    ),
                    "400": ResponseObject(description="Invalid ID supplied"),
                    "404": ResponseObject(description="Pet not found"),
                    "405": ResponseObject(description="Validation exception"),
                },
                security=common_security,
                tags=["pet"]
            ),
            post=OperationObject(
                operation_id="addPet",
                summary="Add a new pet to the store",
                description="Add a new pet to the store",
                request_body=RequestBodyObject(
                    description="Create a new pet in the store",
                    required=True,
                    content={
                        "application/json": MediaTypeObject(schema_=pet_schema),
                        "application/x-www-form-urlencoded": MediaTypeObject(schema_=pet_schema),
                        "application/xml": MediaTypeObject(schema_=pet_schema)
                    },
                ),
                responses={
                        "200": ResponseObject(
                            description="Successful operation",
                            content={
                                "application/json": MediaTypeObject(schema_=pet_schema),
                                "application/xml": MediaTypeObject(schema_=pet_schema),
                            }
                        ),
                        "405": ResponseObject(description="Invalid input"),
                    },
                security=common_security,
                tags=["pet"]
            )
        ),
        "/pet/findByStatus": PathItemObject(
            get=OperationObject(
                operation_id="findPetsByStatus",
                summary="Finds Pets by status",
                description="Multiple status values can be provided with comma separated strings",
                parameters=[
                    ParameterObject(
                        name="status",
                        in_="query",
                        description="Status values that need to be considered for filter",
                        required=False,
                        schema_={
                            "type": "string",
                            "default": "available",
                            "enum": [
                                "available",
                                "pending",
                                "sold", 
                            ]
                        },
                        explode=True
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_={
                                "type": "array",
                                "items": pet_schema
                            }),
                            "application/xml": MediaTypeObject(schema_={
                                "type": "array",
                                "items": pet_schema
                            }),
                        }
                    ),
                    "400": ResponseObject(
                        description="Invalid status value"
                    )
                },
                security=common_security,
                tags=["pet"]
            )
        ),
        "/pet/findByTags": PathItemObject(
            get=OperationObject(
                operation_id="findPetsByTags",
                summary="Finds Pets by tags",
                description="Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.",
                parameters=[
                    ParameterObject(
                        name="tags",
                        in_="query",
                        description="Tags to filter by",
                        required=False,
                        schema_={
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        explode=True
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_={
                                "type": "array",
                                "items": pet_schema
                            }),
                            "application/xml": MediaTypeObject(schema_={
                                "type": "array",
                                "items": pet_schema
                            }),
                        }
                    ),
                    "400": ResponseObject(
                        description="Invalid tag value"
                    )
                },
                security=common_security,
                tags=["pet"]
            )
        ),
        "/pet/{petId}": PathItemObject(
            get=OperationObject(
                operation_id="getPetById",
                summary="Find pet by ID",
                description="Returns a single pet",
                parameters=[
                    ParameterObject(
                        name="petId",
                        in_="path",
                        description="ID of pet to return",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=pet_schema),
                            "application/xml": MediaTypeObject(schema_=pet_schema),
                        }
                    ),
                    "400": ResponseObject(
                        description="Invalid ID supplied"
                    ),
                    "404": ResponseObject(
                        description="Pet not found"
                    )
                },
                security=[
                    {
                        "api_key": []
                    },
                    common_security[0]
                ],
                tags=["pet"]
            ),
            post=OperationObject(
                operation_id="updatePetWithForm",
                summary="Updates a pet in the store with form data",
                description="",
                parameters=[
                    ParameterObject(
                        name="petId",
                        in_="path",
                        description="ID of pet that needs to be updated",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    ),
                    ParameterObject(
                        name="name",
                        in_="query",
                        description="Name of pet that needs to be updated",
                        schema_={
                            "type": "string"
                        }
                    ),
                    ParameterObject(
                        name="status",
                        in_="query",
                        description="Status of pet that needs to be updated",
                        schema_={
                            "type": "string"
                        }
                    )
                ],
                responses={
                    "405": ResponseObject(
                        description="Invalid input"
                    )
                },
                security=common_security,
                tags=["pet"]
            ),
            delete=OperationObject(
                operation_id="deletePet",
                summary="Deletes a pet",
                description="",
                parameters=[
                    ParameterObject(
                        name="api_key",
                        in_="header",
                        description="",
                        required=False,
                        schema_={
                            "type": "string"
                        }
                    ),
                    ParameterObject(
                        name="petId",
                        in_="path",
                        description="Pet id to delete",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    ),
                ],
                responses={
                    "400": ResponseObject(description="Invalid pet value")
                },
                security=common_security,
                tags=["pet"]
            )
        ),
        "/pet/{petId}/uploadImage": PathItemObject(
            post=OperationObject(
                operation_id="uploadFile",
                summary="uploads an image",
                description="",
                parameters=[
                    ParameterObject(
                        name="petId",
                        in_="path",
                        description="ID of pet to update",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    ),
                    ParameterObject(
                        name="additionalMetadata",
                        in_="query",
                        description="Additional Metadata",
                        required=False,
                        schema_={
                            "type": "string"
                        }
                    )
                ],
                request_body=RequestBodyObject(content={"application/octet-stream": {}}),
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(
                                schema_= api_response_schema
                            )
                        }
                    )
                },
                security=common_security,
                tags=["pet"]
            )
        ),
        "/store/inventory": PathItemObject(
            get=OperationObject(
                operation_id="getInventory",
                summary="Returns pet inventories by status",
                description="Returns a map of status codes to quantities",
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(
                                schema_={
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "integer",
                                        "format": "int32"
                                    }
                                }
                            )
                        }
                    )
                },
                security=[
                    {"api_key":[]}
                ],
                tags=["store"]
            )
        ),
        "/store/order": PathItemObject(
            post=OperationObject(
                operation_id="placeOrder",
                summary="Place an order for a pet",
                description="Place a new order in the store",
                request_body=RequestBodyObject(
                    content={
                        "application/json": MediaTypeObject(schema_=order_schema),
                        "application/x-www-form-urlencoded": MediaTypeObject(schema_=order_schema),
                        "application/xml": MediaTypeObject(schema_=order_schema)
                    }
                ),
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=order_schema)
                        }
                    ),
                    "405": ResponseObject(description="Invalid input")
                },
                tags=["store"]
            )
        ),
        "/store/order/{orderId}": PathItemObject(
            get=OperationObject(
                operation_id="getOrderById",
                summary="Find purchase order by ID",
                description="For valid response try integer IDs with value <= 5 or > 10. Other values will generate exceptions.",
                parameters=[
                    ParameterObject(
                        name="orderId",
                        in_="path",
                        description="ID of order that needs to be fetched",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=order_schema),
                            "application/xml": MediaTypeObject(schema_=order_schema),
                        }
                    ),
                    "400": ResponseObject(description="Invalid ID supplied"),
                    "404": ResponseObject(description="Order not found")
                },
                tags=["store"]
            ),
            delete=OperationObject(
                operation_id="deleteOrder",
                summary="Delete purchase order by ID",
                description="For valid response try integer IDs with value < 1000. Anything above 1000 or nonintegers will generate API errors",
                parameters=[
                    ParameterObject(
                        name="orderId",
                        in_="path",
                        description="ID of the order that needs to be deleted",
                        required=True,
                        schema_={
                            "type": "integer",
                            "format": "int64"
                        }
                    )
                ],
                responses={
                    "400": ResponseObject(description="Invalid ID supplied"),
                    "404" : ResponseObject(description="Order not found")
                },
                tags=["store"]
            )
        ),
        "/user": PathItemObject(
            post=OperationObject(
                operation_id="createUser",
                summary="Create user",
                description="This can only be done by the logged in user.",
                request_body=RequestBodyObject(
                    description="Created user object",
                    content={
                        "application/json": MediaTypeObject(schema_=user_schema),
                        "application/x-www-form-urlencoded": MediaTypeObject(schema_=user_schema),
                        "application/xml": MediaTypeObject(schema_=user_schema)
                    }
                ),
                responses={
                    "default": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=user_schema),
                            "application/xml": MediaTypeObject(schema_=user_schema)
                        }
                    ),
                },
                tags=["user"]
            )
        ),
        "/user/createWithList": PathItemObject(
            post=OperationObject(
                operation_id="createUsersWithListInput",
                summary="Creates list of users with given input array",
                description="Creates list of users with given input array",
                request_body=RequestBodyObject(content={
                    "application/json": MediaTypeObject(
                        schema_={
                            "type": "array",
                            "items": user_schema
                        }
                    )
                }),
                responses={
                    "200": ResponseObject(
                        description="Successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=user_schema),
                            "application/xml": MediaTypeObject(schema_=user_schema)
                        }
                    ),
                    "default": ResponseObject(description="successful operation")
                },
                tags=["user"]
            )
        ),
        "/user/login": PathItemObject(
            get=OperationObject(
                operation_id="loginUser",
                summary="Logs user into the system",
                description="",
                parameters=[
                    ParameterObject(
                        name="username",
                        in_="query",
                        description="The user name for login",
                        required=False,
                        schema_={"type": "string"},
                    ),
                    ParameterObject(
                        name="password",
                        in_="query",
                        description="The password for login in clear text",
                        required=False,
                        schema_={"type": "string"}
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        headers={
                            "X-Rate-Limit": HeaderObject(
                                description="calls per hour allowed by the user",
                                schema_={
                                    "type": "integer",
                                    "format": "int32"
                                }
                            ),
                            "X-Expires-After": HeaderObject(
                                description="date in UTC when token expires",
                                schema_={
                                    "type": "string",
                                    "format": "date-time"
                                }
                            )
                        },
                        content={
                            "application/json": MediaTypeObject(schema_={"type": "string"}),
                            "application/xml": MediaTypeObject(schema_={"type": "string"})
                        }
                    ),
                    "400": ResponseObject(description="Invalid username/password supplied")
                },
                tags=["user"]
            )
        ),
        "/user/logout": PathItemObject(
            get=OperationObject(
                operation_id="logoutUser",
                summary="Logs out current logged in user session",
                description="",
                parameters=[],
                responses={
                    "default": ResponseObject(description="successful operation"),
                },
                tags=["user"]
            )
        ),
        "/user/{username}": PathItemObject(
            get=OperationObject(
                operation_id="getUserByName",
                summary="Get user by user name",
                description="",
                parameters=[
                    ParameterObject(
                        name="username",
                        in_="path",
                        description="The name that needs to be fetched. Use user1 for testing. ",
                        required=True,
                        schema_={"type": "string"}
                    )
                ],
                responses={
                    "200": ResponseObject(
                        description="successful operation",
                        content={
                            "application/json": MediaTypeObject(schema_=user_schema),
                            "application/xml": MediaTypeObject(schema_=user_schema)
                        }
                    ),
                    "400": ResponseObject(description="Invalid username supplied"),
                    "404": ResponseObject(description="User not found")
                },
                tags=["user"]
            ),
            put=OperationObject(
                operation_id="updateUser",
                summary="Update user",
                description="This can only be done by the logged in user.",
                parameters=[
                    ParameterObject(
                        name="username",
                        in_="path",
                        description="name that needs to be updated",
                        required=True,
                        schema_={"type":"string"}
                    )
                ],
                request_body=RequestBodyObject(
                    description="Update an existent user in the store",
                    content={
                        "application/json": MediaTypeObject(schema_=user_schema),
                        "application/x-www-form-urlencoded": MediaTypeObject(schema_=user_schema),
                        "application/xml": MediaTypeObject(schema_=user_schema)
                    }
                ),
                responses={
                    "default": ResponseObject(description="successful operation"),
                },
                tags=["user"]
            ),
            delete=OperationObject(
                operation_id="deleteUser",
                summary="Delete user",
                description="This can only be done by the logged in user.",
                parameters=[
                    ParameterObject(
                        name="username",
                        in_="path",
                        description="The name that needs to be deleted",
                        required=True,
                        schema_={"type": "string"}
                    )
                ],
                responses={
                    "400": ResponseObject(description="Invalid username supplied"),
                    "404": ResponseObject(description="User not found")
                },
                tags=["user"]
            )
        )
    }

def test_servers(spec_id, openapi_object):
    servers = [ServerObject(base_url="/api/v3")]
    assert openapi_object.servers == servers

def test_paths(openapi_object, paths):
    assert openapi_object.paths == paths