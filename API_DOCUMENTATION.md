# LiteLLM MCP Server API Documentation

---

## 1. **Server Overview**

The LiteLLM MCP (Model Completion Protocol) Server is a high-performance API designed to interact with large language models (LLMs). It provides tools for generating text completions and retrieving information about supported models. The server is optimized for performance with features like HTTP/2, connection pooling, configurable timeouts, and retry logic. It currently supports GPT-4o and Claude models, making it a versatile solution for various natural language processing tasks.

---

## 2. **Available Tools**

### **2.1 `complete` Tool**
The `complete` tool sends a completion request to a specified LLM model and returns the generated text.

#### **Endpoint**
`POST /v1/complete`

#### **Request Parameters**
- **model** (string, required): The model to use for the completion (e.g., `gpt-4o`, `claude`).
- **prompt** (string, required): The input text or prompt for the model.
- **max_tokens** (integer, optional): The maximum number of tokens to generate.
- **temperature** (float, optional): Sampling temperature for randomness (default: 1.0).
- **top_p** (float, optional): Nucleus sampling probability (default: 1.0).
- **stop** (array of strings, optional): List of stop sequences to end the generation.

#### **Response**
- **id** (string): Unique identifier for the request.
- **model** (string): The model used for the completion.
- **choices** (array): List of generated completions.
  - **text** (string): The generated text.
  - **finish_reason** (string): Reason for completion termination (e.g., `stop`, `length`).

#### **Example Request**
```json
POST /v1/complete
{
  "model": "gpt-4o",
  "prompt": "Write a poem about the ocean.",
  "max_tokens": 50,
  "temperature": 0.7,
  "stop": ["\n"]
}
```

#### **Example Response**
```json
{
  "id": "abc123",
  "model": "gpt-4o",
  "choices": [
    {
      "text": "The ocean whispers secrets to the shore, a timeless dance of waves and lore.",
      "finish_reason": "stop"
    }
  ]
}
```

---

### **2.2 `list_models` Tool**
The `list_models` tool retrieves a list of all supported models.

#### **Endpoint**
`GET /v1/models`

#### **Response**
- **models** (array): List of supported models.
  - **id** (string): Model identifier (e.g., `gpt-4o`, `claude`).
  - **description** (string): A brief description of the model.

#### **Example Request**
```json
GET /v1/models
```

#### **Example Response**
```json
{
  "models": [
    {
      "id": "gpt-4o",
      "description": "GPT-4 optimized for high performance and accuracy."
    },
    {
      "id": "claude",
      "description": "Claude model for conversational AI tasks."
    }
  ]
}
```

---

## 3. **Request/Response Formats**

### **Request Format**
All requests must be in JSON format. Ensure the `Content-Type` header is set to `application/json`.

### **Response Format**
Responses are returned in JSON format with the following structure:
- **success** (boolean): Indicates if the request was successful.
- **data** (object): Contains the response data (if successful).
- **error** (object): Contains error details (if unsuccessful).

---

## 4. **Authentication**

### **API Key Authentication**
To authenticate with the MCP server, include your API key in the `Authorization` header as a Bearer token.

#### **Example Header**
```
Authorization: Bearer YOUR_API_KEY
```

---

## 5. **Error Handling**

### **Common Error Codes**
- **400 Bad Request**: Invalid input parameters.
- **401 Unauthorized**: Missing or invalid API key.
- **404 Not Found**: Requested resource not found.
- **429 Too Many Requests**: Rate limit exceeded.
- **500 Internal Server Error**: Server encountered an error.

### **Example Error Response**
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Invalid 'model' parameter."
  }
}
```

---

## 6. **Rate Limiting**

The MCP server enforces rate limits to ensure fair usage:
- **Requests per minute**: 60
- **Burst limit**: 10 requests in quick succession

If the rate limit is exceeded, a `429 Too Many Requests` error is returned.

---

## 7. **Best Practices**

- Use connection pooling to reduce latency.
- Set appropriate timeouts to handle network delays.
- Cache the list of models to avoid frequent `list_models` calls.
- Use the `stop` parameter to control the length of completions.

---

## 8. **Code Examples**

### **Python**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://lite-llm-mcp-server.com/v1"

# Example: Completion Request
headers = {"Authorization": f"Bearer {API_KEY}"}
data = {
    "model": "gpt-4o",
    "prompt": "Write a poem about the ocean.",
    "max_tokens": 50,
    "temperature": 0.7
}

response = requests.post(f"{BASE_URL}/complete", json=data, headers=headers)
print(response.json())
```

### **JavaScript**
```javascript
const axios = require('axios');

const API_KEY = "YOUR_API_KEY";
const BASE_URL = "https://lite-llm-mcp-server.com/v1";

// Example: Completion Request
const headers = { Authorization: `Bearer ${API_KEY}` };
const data = {
  model: "gpt-4o",
  prompt: "Write a poem about the ocean.",
  max_tokens: 50,
  temperature: 0.7
};

axios.post(`${BASE_URL}/complete`, data, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error.response.data));
```

### **curl**
```bash
curl -X POST https://lite-llm-mcp-server.com/v1/complete \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
  "model": "gpt-4o",
  "prompt": "Write a poem about the ocean.",
  "max_tokens": 50,
  "temperature": 0.7
}'
```

---

## 9. **Model-specific Information**

### **GPT-4o**
- Optimized for high performance and accuracy.
- Suitable for general-purpose text generation.

### **Claude**
- Designed for conversational AI tasks.
- Excels in dialogue and context understanding.

---

## 10. **Performance Tips**

- **Enable HTTP/2**: Use HTTP/2 for faster request/response cycles.
- **Reuse Connections**: Use persistent connections to reduce latency.
- **Optimize Prompts**: Keep prompts concise to reduce token usage.
- **Leverage `max_tokens`**: Set a reasonable `max_tokens` value to control response size.
- **Retry Logic**: Implement retry logic for transient errors (e.g., 500 or network timeouts).

---

This documentation provides a comprehensive guide to using the LiteLLM MCP Server effectively. For further assistance, contact support or refer to the official developer portal. 