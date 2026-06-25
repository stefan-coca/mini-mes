from openai import OpenAI
from tools import *
import json

client = OpenAI()

FUNCTION_MAP = {
    "get_today_count": get_today_count,
    "get_machine_status": get_machine_status,
    "get_last_piece": get_last_piece,
    "get_fault_today": get_fault_today,
    "get_recent_logs": get_recent_logs,
    "get_state_events_today": get_state_events_today,
    "get_production_count": get_production_count,
}

TOOLS = [
    {
        "type": "function",
        "name": "get_production_count",
        "description": (
            "Returns the number of produced parts. "
            "Use this function whenever the user asks how many parts were produced. "
            "The filters machine, date and shift are optional. "
            "If the user only mentions yesterday, only provide date='yesterday'. "
            "If the user only mentions today, only provide date='today'. "
            "Do not ask the user for missing filters."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "machine": {
                    "type": "string",
                    "description": "Optional machine name, e.g. A2."
                },
                "date": {
                    "type": "string",
                    "description": "Optional. Use 'today', 'yesterday' or YYYY-MM-DD."
                },
                "shift": {
                    "type": "integer",
                    "description": "Optional shift number."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_machine_status",
        "description": "Returneaza statusul curent al masinii"
    },
    {
        "type": "function",
        "name": "get_last_piece",
        "description": "Returneaza timestamp-ul ultimei piese produse"
    },
    {
        "type": "function",
        "name": "get_fault_today",
        "description": "Returneaza durata totala a faulturilor de astazi in minute"
    },
    {
        "type": "function",
        "name": "get_recent_logs",
        "description": "Returneaza ultimele evenimente din logul sistemului"
    },
    {
        "type": "function",
        "name": "get_state_events_today",
        "description": "Returneaza toate evenimentele RUNNING, STOPPED si FAULT din ziua curenta"
    }
]

while True:

    question = input("\nTu: ")

    if question.lower() == "exit":
        break

    response = client.responses.create(
        model="gpt-5",
        tools=TOOLS,
        instructions="""
    You are the AI assistant of a Manufacturing Execution System (MES).

    Always use the available tools to answer questions about:
    - production
    - machine status
    - faults
    - machine events
    - logs

    Do not ask the user for additional filters unless they are truly required.

    The function get_production_count() accepts optional filters:
    - machine
    - date
    - shift

    Examples:
    - "How many parts were produced today?" -> date="today"
    - "How many parts were produced yesterday?" -> date="yesterday"
    - "How many parts were produced yesterday on A2?" -> machine="A2", date="yesterday"
    - "How many parts were produced on shift 2?" -> shift=2

    If the user does not specify a machine or shift, do not invent them.
    Simply call the function with the information that is available.
    """,
        input=question
    )

    tool_results = {}

    for item in response.output:

        if item.type == "function_call":

            print("GPT a cerut:", item.name)

            arguments = json.loads(item.arguments)

            result = FUNCTION_MAP[item.name](**arguments)

            tool_results[item.name] = result

    if tool_results:

        final_response = client.responses.create(
            model="gpt-5",
            input=f"""
    Utilizatorul a intrebat:

    {question}

    Rezultatele tool-urilor sunt:

    {tool_results}

    Raspunde utilizatorului in romana.
    """
        )

        print("\nAgent:")
        print(final_response.output_text)
