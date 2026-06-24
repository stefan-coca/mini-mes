from openai import OpenAI
from tools import *

client = OpenAI()

FUNCTION_MAP = {
    "get_today_count": get_today_count,
    "get_machine_status": get_machine_status,
    "get_last_piece": get_last_piece,
    "get_fault_today": get_fault_today,
    "get_recent_logs": get_recent_logs,
    "get_state_events_today": get_state_events_today,
}

TOOLS = [
    {
        "type": "function",
        "name": "get_today_count",
        "description": "Returneaza numarul de piese produse astazi"
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
        input=question
    )

    tool_results = {}

    for item in response.output:

        if item.type == "function_call":

            print("GPT a cerut:", item.name)

            result = FUNCTION_MAP[item.name]()

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
