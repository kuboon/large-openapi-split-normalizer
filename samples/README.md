# OpenAPI Schema Samples

This directory contains sample OpenAPI schema files that demonstrate circular references and different file organization strategies.

## Purpose

These samples are used to:
- Test the OpenAPI schema $ref resolution functionality
- Demonstrate circular references (User ↔ Organization)
- Show both single-file and multi-file organization approaches
- Validate that both approaches represent the same API structure

## Directory Structure

```
samples/
├── single-file/
│   └── openapi.yaml           # Complete API in a single file
└── multi-file/
    ├── openapi.yaml           # Main entry point with $ref references
    ├── components/
    │   └── schemas/           # Schema definitions
    │       ├── User.yaml
    │       ├── UserInput.yaml
    │       ├── Organization.yaml
    │       ├── OrganizationInput.yaml
    │       └── Error.yaml
    └── paths/                 # Path/endpoint definitions
        ├── users.yaml
        ├── users_by_id.yaml
        ├── organizations.yaml
        └── organizations_by_id.yaml
```

## Single-File Version

**Location**: `samples/single-file/openapi.yaml`

A complete OpenAPI 3.0.3 specification in a single file. All schemas, paths, and components are defined in one YAML document. Internal references use JSON Pointer notation (e.g., `#/components/schemas/User`).

**Features**:
- ✅ Circular references: User → Organization → User
- ✅ Complete API definition
- ✅ All schemas inline
- ✅ Easy to read and understand
- ✅ No external file dependencies

## Multi-File Version

**Location**: `samples/multi-file/`

The same API specification split across multiple files organized by type. This approach is more maintainable for large APIs with 100+ schema files.

**Features**:
- ✅ Same circular references: User → Organization → User
- ✅ Modular file structure
- ✅ Relative path $ref references
- ✅ Subdirectory organization
- ✅ File-to-file references
- ✅ Represents identical structure to single-file version

**Reference Types Used**:
1. **Main file to paths**: `$ref: './paths/users.yaml'`
2. **Main file to schemas**: `$ref: './components/schemas/User.yaml'`
3. **Path files to schemas**: `$ref: '../components/schemas/User.yaml'`
4. **Schema to schema** (circular): `$ref: './Organization.yaml'` and `$ref: './User.yaml'`

## Circular Reference Pattern

Both versions implement the same circular reference pattern:

```yaml
User:
  properties:
    organization:
      $ref: Organization  # User references Organization

Organization:
  properties:
    owner:
      $ref: User        # Organization references User (circular!)
    members:
      type: array
      items:
        $ref: User      # Also references User in array
```

This creates a circular dependency: User → Organization → User

## API Overview

The sample API is a user and organization management system with the following endpoints:

### User Endpoints
- `GET /users` - List all users
- `POST /users` - Create a new user
- `GET /users/{userId}` - Get user by ID

### Organization Endpoints
- `GET /organizations` - List all organizations
- `POST /organizations` - Create a new organization
- `GET /organizations/{orgId}` - Get organization by ID

### Schemas
- **User**: User entity with reference to Organization
- **UserInput**: Input schema for creating users
- **Organization**: Organization entity with references to User (owner and members)
- **OrganizationInput**: Input schema for creating organizations
- **Error**: Standard error response

## Testing with OpenAPI Tools

You can validate these schemas using standard OpenAPI tools:

### Using Swagger Editor Online
1. Visit https://editor.swagger.io/
2. Copy the content of `samples/single-file/openapi.yaml`
3. Paste into the editor
4. View the generated documentation

### Using OpenAPI CLI Tools

```bash
# Validate the single-file schema
npx @redocly/cli lint samples/single-file/openapi.yaml

# Bundle the multi-file schema into a single file
npx @redocly/cli bundle samples/multi-file/openapi.yaml -o bundled.yaml

# Validate the multi-file schema
npx @redocly/cli lint samples/multi-file/openapi.yaml
```

### Using Swagger UI

```bash
# Serve with Swagger UI
docker run -p 80:8080 -e SWAGGER_JSON=/foo/openapi.yaml \
  -v /path/to/samples/single-file:/foo swaggerapi/swagger-ui
```

## Expected Behavior

When processed by an OpenAPI $ref resolver:

1. **Single-file version**: Internal references (`#/components/schemas/...`) should be resolved
2. **Multi-file version**: 
   - External file references should be loaded
   - Relative paths should be resolved correctly
   - Circular references should be detected and handled appropriately
3. **Both versions**: Should produce equivalent resolved schemas

## Use Cases

These samples are useful for:
- Testing $ref resolution logic
- Demonstrating circular reference handling
- Showing file organization best practices
- Validating multi-file bundling tools
- Teaching OpenAPI schema design patterns

## Notes

- Both versions use OpenAPI 3.0.3 specification
- Circular references are intentional and represent a common real-world pattern
- The multi-file version uses relative paths exclusively
- All $ref references use local file paths (no HTTP URLs)
- The structure is kept simple while demonstrating key concepts

## Future Enhancements

Potential additions to these samples:
- More complex circular reference chains (A → B → C → A)
- Nested subdirectories for deeper file organization
- Examples with both YAML and JSON formats
- Additional reference patterns (allOf, oneOf, anyOf with $ref)
- Examples with security schemes and reusable parameters
