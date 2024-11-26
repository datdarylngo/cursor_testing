from flask import Flask, request, jsonify, render_template
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanContext, set_span_in_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the parent directory
load_dotenv(dotenv_path='../.env')

# Get and verify API keys and configuration
api_key = os.getenv('OPENAI_API_KEY')
arize_api_key = os.getenv('ARIZE_API_KEY')
arize_space_id = os.getenv('ARIZE_SPACE_ID')
model_id = os.getenv('ARIZE_MODEL_ID')
phoenix_api_key = os.getenv('PHOENIX_API_KEY')
phoenix_project = os.getenv('PHOENIX_PROJECT_NAME')
enable_propagation = os.getenv('ENABLE_CONTEXT_PROPAGATION', 'false').lower() == 'true'

logger.info(f"Context propagation is {'enabled' if enable_propagation else 'disabled'}")

# Set Phoenix environment variables
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={phoenix_api_key}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

# Import open-telemetry dependencies
from arize_otel import register_otel, Endpoints
from phoenix.otel import register as phoenix_register
from openinference.instrumentation.openai import OpenAIInstrumentor

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

# Instrument OpenAI calls with Phoenix tracer provider
OpenAIInstrumentor().instrument(tracer_provider=phoenix_tracer_provider)

logger.info("OpenAI instrumentation complete with Phoenix tracer")

app = Flask(__name__)

# Configure OpenAI
client = OpenAI(
    api_key=api_key
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    try:
        # Get context if propagation is enabled
        context = None
        if enable_propagation:
            logger.info("Extracting propagated context from headers")
            context = extract(request.headers)
        else:
            logger.info("Context propagation disabled - starting new trace")
        
        # Start span with or without context
        with tracer.start_as_current_span(
            "llm_gateway_process",
            context=context if enable_propagation else None
        ) as span:
            data = request.get_json()
            text = data.get('text')
            
            if not text:
                return jsonify({"error": "No text provided"}), 400
            
            span.set_attribute("input.text", text)
            logger.info(f"Received text for processing: {text}")
            logger.info("Sending request to OpenAI...")
            
            # Call OpenAI API with new syntax
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content
            
            result = {
                "original_text": text,
                "ai_response": ai_response
            }
            
            span.set_attribute("output.response", ai_response)
            
            logger.info("Successfully received response from OpenAI")
            logger.info(f"Original Text: {text}")
            logger.info(f"AI Response: {ai_response}")
            logger.info("Trace data sent to Arize and Phoenix")
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        if 'span' in locals():
            span.set_attribute("error", str(e))
            span.record_exception(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting LLM Gateway Service on port 5001...")
    app.run(port=5001, debug=True) 