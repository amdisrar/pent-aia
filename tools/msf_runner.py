import os
from dotenv import load_dotenv
from pymetasploit3.msfrpc import MsfRpcClient

load_dotenv()

def _get_client():
    return MsfRpcClient(
        password=os.environ["MSF_PASS"],
        username=os.environ["MSF_USER"],
        server=os.environ["MSF_HOST"],
        port=int(os.environ["MSF_PORT"]),
        ssl=os.environ["MSF_SSL"].lower() == "true"
    )

def search_msf_modules(keyword: str) -> list:
    try:
        client = _get_client()
        return client.modules.search(keyword)
    except Exception as e:
        return [f"Search error: {str(e)}"]

def run_msf_module(module_type: str, module_name: str, params: dict) -> str:
    try:
        client = _get_client()
        module = client.modules.use(module_type, module_name)
        for k, v in params.items():
            module[k] = v
        console = client.consoles.console()
        output = console.run_module_with_output(module)
        return output.strip()
    except Exception as e:
        return f"Module run error: {str(e)}"

def exploit_with_payload(exploit_name: str, payload_name: str, exploit_args: dict, payload_args: dict) -> str:
    try:
        client = _get_client()
        exploit = client.modules.use('exploit', exploit_name)
        exploit.payload = payload_name

        for k, v in exploit_args.items():
            exploit[k] = v
        for k, v in payload_args.items():
            exploit[k] = v

        console = client.consoles.console()
        return console.run_module_with_output(exploit).strip()
    except Exception as e:
        return f"Exploit error: {str(e)}"

def list_sessions() -> dict:
    try:
        client = _get_client()
        return client.sessions.list
    except Exception as e:
        return {"error": str(e)}

def interact_session(session_id: int, command: str) -> str:
    try:
        client = _get_client()
        session = client.sessions.session(session_id)
        return session.run_with_output(command).strip()
    except Exception as e:
        return f"Session error: {str(e)}"