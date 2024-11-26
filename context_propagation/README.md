# Context Propagation Demo

This project demonstrates service-to-service communication between two Python services with OpenTelemetry context propagation.

## Project Structure

context_propagation/
├── .env                    # Environment variables
├── python_application/     # First service (Client)
│   ├── requirements.txt
│   ├── application.py     # Initiates traces and propagates context
│   └── templates/
│       └── index.html
└── python_gateway/        # Second service (Gateway to OpenAI)
    ├── requirements.txt
    ├── llm_gateway.py     # Receives context and continues traces
    └── templates/
        └── index.html

## Context Propagation Implementation

This project demonstrates distributed tracing with context propagation between two services:

### Application Service (Initiator)
1. Creates parent span "application_process_request"
2. Creates child span "gateway_request"
3. Injects trace context into headers using OpenTelemetry's inject()
4. Sends request to Gateway Service with propagated context

Key code for context propagation in application.py:
```python
# Import for context propagation
from opentelemetry.propagate import inject

# Create headers and inject trace context
headers = {"Content-Type": "application/json"}
inject(headers)  # Injects current trace context into headers

# Send request with propagated context
response = requests.post(
    GATEWAY_SERVICE_URL,
    headers=headers,  # Headers contain the trace context
    json={"text": text}
)
```

### Gateway Service (Receiver)
1. Extracts trace context from incoming request headers
2. Creates new span linked to the application's trace
3. Processes the request within the context
4. Automatically traces OpenAI API calls

Key code for context propagation in llm_gateway.py:
```python
# Imports for context propagation
from opentelemetry.propagate import extract

# Extract context and create span
context = extract(request.headers)
with tracer.start_as_current_span(
    "llm_gateway_process",
    context=context  # Links this span to application's trace
) as span:
    # Process request...
```

## Tracing Flow
1. Application Service starts a trace
2. Context is propagated to Gateway Service
3. Gateway Service continues the same trace
4. All spans appear under the same trace ID in observability tools

## Observability Setup

The project is configured to send traces to two observability platforms:
1. Arize
2. Arize Phoenix

Both services use the same configuration to ensure traces are properly connected:
- Same model_id
- Same project configuration
- Consistent span naming and attributes

## Running the Services

1. **Start the Gateway Service first:**
   ```bash
   cd python_gateway
   python llm_gateway.py    # Runs on http://localhost:5001
   ```

2. **Start the Application Service:**
   ```bash
   cd python_application
   python application.py    # Runs on http://localhost:5000
   ```

## Viewing Traces

After making a request through the application:
1. Check Arize Phoenix UI for immediate trace visibility
2. View the complete trace showing:
   - Parent span from Application Service
   - Child span from Application Service
   - Connected span from Gateway Service
   - OpenAI API call spans

## Common Issues & Troubleshooting

1. **Separate Trace IDs**
   - Verify headers are being properly injected and extracted
   - Check both services are using the same tracer configuration
   - Ensure all required OpenTelemetry dependencies are installed

2. **Missing Spans**
   - Verify both services are properly initialized with tracers
   - Check span attributes and names
   - Ensure proper error handling in spans

3. **Context Loss**
   - Verify headers are not being modified in transit
   - Check context extraction in Gateway Service
   - Ensure proper span creation with context

## Next Steps
- Add more detailed span attributes
- Implement error tracking across services
- Add metrics collection
- Enhance logging correlation
