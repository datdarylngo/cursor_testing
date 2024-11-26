from flask import Flask, request, jsonify, render_template
import requests
import logging
from opentelemetry import trace
from opentelemetry.propagate import inject
from arize_otel import register_otel, Endpoints
from phoenix.otel import register as phoenix_register
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path='../.env')

# Get credentials and configuration
arize_api_key = os.getenv('ARIZE_API_KEY')
arize_space_id = os.getenv('ARIZE_SPACE_ID')
model_id = os.getenv('ARIZE_MODEL_ID')
phoenix_api_key = os.getenv('PHOENIX_API_KEY')
phoenix_project = os.getenv('PHOENIX_PROJECT_NAME')
enable_propagation = os.getenv('ENABLE_CONTEXT_PROPAGATION', 'false').lower() == 'true'

logger.info(f"Context propagation is {'enabled' if enable_propagation else 'disabled'}")

if not all([arize_api_key, arize_space_id, phoenix_api_key]):
    raise ValueError("Missing required API keys in environment variables")

logger.info("Initializing Arize and Phoenix OpenTelemetry integration...")

# Set Phoenix environment variables
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={phoenix_api_key}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

# Setup Arize OTEL
register_otel(
    endpoints=Endpoints.ARIZE,
    space_id=arize_space_id,
    api_key=arize_api_key,
    model_id=model_id,
)

logger.info("Arize OpenTelemetry setup complete")

# Setup Phoenix OTEL with tracer provider
phoenix_tracer_provider = phoenix_register(
    project_name=phoenix_project,
    endpoint="https://app.phoenix.arize.com/v1/traces"
)

logger.info("Phoenix OpenTelemetry setup complete")

# Get tracer from Phoenix tracer provider
tracer = phoenix_tracer_provider.get_tracer(__name__)

app = Flask(__name__)

GATEWAY_SERVICE_URL = "http://localhost:5001/process"  # Gateway service endpoint

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-to-llm', methods=['POST'])
def send_to_llm():
    try:
        # Always create traces, regardless of propagation setting
        with tracer.start_as_current_span("application_process_request") as parent_span:
            data = request.get_json()
            text = data.get('text')
            
            if not text:
                return jsonify({"error": "No text provided"}), 400
            
            # Add attributes to parent span
            parent_span.set_attribute("text.length", len(text))
            parent_span.set_attribute("service.name", "application_service")
            parent_span.set_attribute("model.name", model_id)
            parent_span.set_attribute("context_propagation_enabled", enable_propagation)
            
            logger.info(f"Application Service: Sending text to LLM Gateway: {text}")
            
            # Always create child span, even if not propagating
            with tracer.start_as_current_span("gateway_request") as child_span:
                # Add attributes to child span
                child_span.set_attribute("gateway.url", GATEWAY_SERVICE_URL)
                child_span.set_attribute("operation", "send_to_gateway")
                child_span.set_attribute("model.name", model_id)
                child_span.set_attribute("input.text", text)
                child_span.set_attribute("context_propagation_enabled", enable_propagation)
                
                # Prepare headers
                headers = {"Content-Type": "application/json"}
                
                # Only inject context if propagation is enabled
                if enable_propagation:
                    logger.info("Injecting trace context into headers")
                    inject(headers)
                    child_span.set_attribute("context_propagated", True)
                else:
                    logger.info("Context propagation disabled - creating independent trace")
                    child_span.set_attribute("context_propagated", False)
                
                # Send request
                response = requests.post(
                    GATEWAY_SERVICE_URL,
                    headers=headers,
                    json={"text": text}
                )
                
                result = response.json()
                
                # Add response attributes to child span
                child_span.set_attribute("gateway.response.status", response.status_code)
                if "error" in result:
                    child_span.set_attribute("gateway.response.error", str(result["error"]))
                else:
                    child_span.set_attribute("output.response", result.get("ai_response", ""))
                
                logger.info(f"Application Service: Received response from LLM Gateway: {result}")
            
            return result
            
    except Exception as e:
        logger.error(f"Application Service Error: {str(e)}")
        if 'parent_span' in locals():
            parent_span.set_attribute("error", str(e))
            parent_span.record_exception(e)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Starting Application Service on port 5000...")
    app.run(port=5000, debug=True) 