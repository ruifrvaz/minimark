# REST API Documentation

## Overview

Welcome to the API documentation! This guide will help you understand how to integrate with our service. Please read through the entire document before getting started.

### Authentication

All API requests require authentication. You need to include your API key in the header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/resource
```

### Base URL

The base URL for all API endpoints is: `https://api.example.com/v1`

## Endpoints

### GET /users

Retrieves a list of users. This endpoint returns paginated results.

**Parameters:**
- `page` (optional): Page number for pagination
- `limit` (optional): Number of results per page (default: 20)

**Response:**

```json
{
  "users": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
  ],
  "pagination": {
    "page": 1,
    "total_pages": 5
  }
}
```

### POST /users

Creates a new user. Please make sure to include all required fields.

**Request Body:**

```json
{
  "name": "New User",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Error Handling

The API returns standard HTTP status codes. Here are the common ones:

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Missing or invalid API key
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Rate Limiting

We limit API requests to 1000 per hour. If you exceed this limit, you will receive a 429 status code. Thank you for being considerate of our resources.

## Best Practices

1. Always validate input data before sending requests
2. Implement exponential backoff for retry logic
3. Cache responses when possible to reduce API calls
4. Use webhooks instead of polling when available

Honestly, following these practices will make your integration much smoother and more reliable.
