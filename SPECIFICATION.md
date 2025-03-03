# CueCode OpenAPI Specification

## Limitations

### OpenAPI Version
CueCode is designed to work with OpenAPI 3.1, the latest OpenAPI Standard. To convert an OpenAPI 3.0 API spec to v3.1, the tool [openapi-format](https://www.npmjs.com/package/openapi-format) can be used.

### OpenAPI Servers
The [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.0.html) allows for an array of servers to be provided for each OpenAPI Operation or Path, and the operations or paths will be valid for each of the provided servers. As it is difficult for the LLM behind CueCode to differentiate between which server is appropriate for creating API calls, only a single server per path operation is supported.

### HTTP Operations
CueCode currently only supports the most common HTTP operations: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

## OpenAPI Specification Extensions

### xCueCode
CueCode allows the use of a custom `x-cuecode` API extension for OpenAPI Paths, Operations, Parameters, and Entities that will allow the LLM to be prompted with more relevant information to create API payloads. If no `x-cuecode` is provided, the item's `description`, then `summary` will be used in that order[^1].

[^1]: This may be subject to change, since testing may prove that prompting with both summary and description is superior to either alone.