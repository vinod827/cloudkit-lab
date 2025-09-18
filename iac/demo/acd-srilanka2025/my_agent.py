import os
import boto3

import logging
from datetime import datetime

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudcostadvisoragent")

from datetime import datetime, timedelta
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient
from botocore.exceptions import ClientError

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-8b-instruct-v1:0")  # Meta's Llama Model

ACTOR_ID = "user_827"
SESSION_ID = "personal_session_827" # Unique session identifier

client = MemoryClient()

# Initialize Memory Client
client = MemoryClient(region_name=REGION)
memory_name = "CloudCostAdvisorAgentMemory"

try:
    # Create memory resource without strategies (thus only access to short-term memory)
    memory = client.create_memory_and_wait(
        name=memory_name,
        strategies=[],  # No strategies for short-term memory
        description="Short-term memory for personal agent",
        event_expiry_days=7, # Retention period for short-term memory. This can be upto 365 days.
    )
    memory_id = memory['id']
    logger.info(f"Created memory: {memory_id}")
except ClientError as e:
    logger.info(f"ERROR: {e}")
    if e.response['Error']['Code'] == 'ValidationException' and "already exists" in str(e):
        # If memory already exists, retrieve its ID
        memories = client.list_memories()
        memory_id = next((m['id'] for m in memories if m['id'].startswith(memory_name)), None)
        logger.info(f"Memory already exists. Using existing memory ID: {memory_id}")
except Exception as e:
    # Show any errors during memory creation
    logger.error(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    # Cleanup on error - delete the memory if it was partially created
    if memory_id:
        try:
            client.delete_memory_and_wait(memory_id=memory_id)
            logger.info(f"Cleaned up memory: {memory_id}")
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up memory: {cleanup_error}")

# ------------------------------------------------------------------------------
# Initialize Bedrock AgentCore App
# ------------------------------------------------------------------------------
app = BedrockAgentCoreApp()

# Configure Bedrock model (AgentCore native)
model = BedrockModel(
    model_id=MODEL_ID,
    streaming=False,
    region_name=REGION,
)

SYSTEM_PROMPT = """
You are Cloud Cost Advisor Agent.
Your job is to help users query AWS cost data and summarize it clearly.
If a user asks about AWS cost (e.g., "last week EC2"), call the cost_explorer tool.
"""


# ------------------------------------------------------------------------------
# Custom Tool
# ------------------------------------------------------------------------------
@tool
def cost_explorer(service: str = "Amazon Elastic Compute Cloud - Compute",
                  days: int = 7) -> dict:
    """
    Fetch AWS cost data for a given service over the last N days.
    Default: EC2 over last 7 days.
    Returns structured JSON for LLM augmentation.
    """
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": start.strftime("%Y-%m-%d"),
            "End": end.strftime("%Y-%m-%d")
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": [service]
            }
        }
    )

    # Collect daily costs
    daily_costs = []
    total = 0.0
    currency = "USD"
    for item in response["ResultsByTime"]:
        amount = float(item["Total"]["UnblendedCost"]["Amount"])
        total += amount
        currency = item["Total"]["UnblendedCost"]["Unit"]
        daily_costs.append({
            "date": item["TimePeriod"]["Start"],
            "amount": round(amount, 2)
        })

    return {
        "service": service,
        "days": days,
        "total_cost": round(total, 2),
        "currency": currency,
        "daily_breakdown": daily_costs
    }

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
   #tools=[cost_explorer]
)

# ------------------------------------------------------------------------------
# Initialize Cost Explorer Client
# ------------------------------------------------------------------------------
ce = boto3.client("ce", region_name=REGION)

@app.entrypoint
def invoke(payload):
    """Main agent entrypoint"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    # return {
    #     "response": result.message
    # }
    return result.message['content'][0]['text']


if __name__ == "__main__":
    app.run()