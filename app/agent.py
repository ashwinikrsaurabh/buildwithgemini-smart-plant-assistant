# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_plant_to_inventory,
    calculate_fertilizer_dosage,
    consult_plant_kb,
    fetch_live_greenhouse_climate,
    find_nearby_places,
    generate_plant_image,
    generate_plant_video,
    geocode_address,
    get_plant_details,
    list_plants_inventory,
    update_plant_care,
)


# Resource name for AgentEngine sandbox code execution
AGENT_ENGINE_RESOURCE_NAME = (
    "projects/549755004699/locations/us-east1/reasoningEngines/5048159149305626624"
)
SANDBOX_RESOURCE_NAME = os.environ.get("SANDBOX_RESOURCE_NAME", None)

sandbox_code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME if not SANDBOX_RESOURCE_NAME else None,
)

# Build A2UI System Prompt using A2uiSchemaManager version 0.8 and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a helpful AI plant and greenhouse assistant backed by a Firestore plant inventory database and a grounded Vertex AI RAG knowledge corpus. "
        "You can look up plant specs and care details, search the grounded plant knowledge corpus (consult_plant_kb) for botanical details and plant care advice, "
        "generate plant and greenhouse images (generate_plant_image), generate short plant and greenhouse videos (generate_plant_video), "
        "execute Python code in a safe AgentEngine sandbox, "
        "list greenhouse inventory, update plant care logs and stock, add new plants to inventory, calculate water/fertilizer dosages, fetch live greenhouse climate data, "
        "geocode street addresses to coordinates using Google Maps Geocoding, and find nearby garden centers, nurseries, and florists using Google Places API (New). "
        "You also remember the user's stated preferences, garden collection, plant issues, and facts from previous "
        "conversations using Memory Bank to personalize your advice and care instructions."
    ),
    workflow_description="Analyze the user request, query plant databases/knowledge bases or call tools, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each agent response to store session memories."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=sandbox_code_executor,
    tools=[
        PreloadMemoryTool(),
        get_plant_details,
        list_plants_inventory,
        update_plant_care,
        add_plant_to_inventory,
        calculate_fertilizer_dosage,
        fetch_live_greenhouse_climate,
        geocode_address,
        find_nearby_places,
        consult_plant_kb,
        generate_plant_image,
        generate_plant_video,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)


app = App(
    root_agent=root_agent,
    name="app",
)


