import os
import time 
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

def exploit_with_payload(
    exploit_name: str,
    payload_name: str,
    exploit_args: dict,
    payload_args: dict
) -> str:
    """
    Launch an exploit with a separate payload object.
    Works for payloads that require LHOST/LPORT, e.g. reverse shells.
    """
    try:
        client = _get_client()

        # 1 – load exploit and payload as separate modules
        exploit = client.modules.use("exploit", exploit_name)
        payload = client.modules.use("payload", payload_name)

        # 2 – set exploit-specific options (RHOSTS, RPORT, etc.)
        for k, v in exploit_args.items():
            exploit[k] = v

        # 3 – set payload-specific options (LHOST, LPORT, etc.)
        for k, v in payload_args.items():
            payload[k] = v

        # 4 – execute exploit with payload -> returns job-id / uuid
        result = exploit.execute(payload=payload)

        # 5 – return a human-readable summary
        return f"Exploit launched: job_id={result['job_id']}, uuid={result['uuid']}"

    except Exception as e:
        return f"Exploit error: {str(e)}"

def list_sessions() -> dict:
    try:
        client = _get_client()
        return client.sessions.list
    except Exception as e:
        return {"error": str(e)}

def interact_session(session_id: int, command: str) -> str:
    """
    Run a shell command in an active Metasploit session.
    Works for both 'shell' and 'meterpreter' sessions.
    """
    try:
        client = _get_client()

        # Metasploit stores keys as strings
        sid = str(session_id)

        if sid not in client.sessions.list.keys():
            return f"Session error: Session ID ({sid}) not found"

        sess = client.sessions.session(sid)
        sess_type = client.sessions.list[sid]["type"]

        # For plain command-shell sessions
        if sess_type == "shell":
            sess.write(command + "\n")
            time.sleep(1)                       # give target time to respond
            return sess.read().strip()

        # For Meterpreter sessions
        if sess_type == "meterpreter" and hasattr(sess, "run_with_output"):
            return sess.run_with_output(command).strip()

        return f"Session error: Unsupported session type '{sess_type}'"

    except Exception as e:
        return f"Session error: {str(e)}"