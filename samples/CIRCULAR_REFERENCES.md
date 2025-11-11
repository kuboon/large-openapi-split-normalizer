# Circular Reference Diagram

This document illustrates the circular references present in both sample schemas.

## Schema Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Circular Reference Pattern                │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────┐
         │     User     │
         ├──────────────┤
         │ id           │
         │ username     │
         │ email        │
    ┌────│ organization │───┐
    │    │ role         │   │
    │    │ createdAt    │   │
    │    │ updatedAt    │   │
    │    └──────────────┘   │
    │                       │
    │  $ref reference       │
    │  (creates cycle)      │
    │                       │
    │    ┌──────────────┐   │
    │    │Organization  │   │
    │    ├──────────────┤   │
    │    │ id           │   │
    │    │ name         │   │
    └───▶│ owner        │◀──┘
         │ members[]    │───┐
         │ industry     │   │
         │ website      │   │
         │ createdAt    │   │
         │ updatedAt    │   │
         └──────────────┘   │
                            │
         ┌──────────────────┘
         │ $ref reference
         │ (also circular,
         │  via array)
         ▼
    ┌──────────────┐
    │     User     │
    │   (same)     │
    └──────────────┘

```

## Reference Paths

### Single-File Version

```yaml
User:
  properties:
    organization:
      $ref: '#/components/schemas/Organization'

Organization:
  properties:
    owner:
      $ref: '#/components/schemas/User'
    members:
      type: array
      items:
        $ref: '#/components/schemas/User'
```

### Multi-File Version

```yaml
# In components/schemas/User.yaml
properties:
  organization:
    $ref: './Organization.yaml'

# In components/schemas/Organization.yaml
properties:
  owner:
    $ref: './User.yaml'
  members:
    type: array
    items:
      $ref: './User.yaml'
```

## Why Circular References?

Circular references are common in real-world APIs where entities have bidirectional relationships:

1. **User belongs to Organization** - A user is a member of an organization
2. **Organization has an owner (User)** - The organization is owned by a user
3. **Organization has members (Users)** - Multiple users can be members

This creates natural circular dependencies that must be handled by any $ref resolution tool.

## Resolution Challenges

When resolving these references:

1. **Infinite expansion risk**: Naive resolution could expand User → Organization → User → Organization... infinitely
2. **Detection**: Tools must detect when they encounter a schema they're already resolving
3. **Handling strategies**:
   - Keep as internal reference after first expansion
   - Use reference markers to prevent infinite loops
   - Limit expansion depth
   - Create shared component definitions

## Testing Significance

These samples are valuable for testing because they:
- Verify cycle detection algorithms work correctly
- Ensure the tool doesn't crash or hang on circular references
- Validate that the resolved schema maintains semantic correctness
- Test both internal (`#/components/...`) and external (`./File.yaml`) circular references
