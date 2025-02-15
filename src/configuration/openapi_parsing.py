"""For parsing OpenAPI spec and converting to CueCode config objects"""

from jsonref import JsonRef #pylint: disable = import-error
from common.models.openapi_server import OpenAPIServer

def make_oa_servers_from_json(oa_servers: list[OpenAPIServer], json: JsonRef): #pylint: disable=import-error
    """
    Build Server objects, only for the top-level "servers" key/object.
    This is in contrast to documented OpenAPI behavior which allows
    one to override the server base path per endpoint. Our prototype
    does not support that behavior.

    We also depart from the spec in that do not support relative paths
    for the server url.

    See https://swagger.io/docs/specification/v3_0/api-host-and-base-path/
    """
    json_servers = json["servers"]
    for s in json_servers:
        print(s)
        oas = OpenAPIServer(url=s["url"])
        oa_servers.append(oas)

