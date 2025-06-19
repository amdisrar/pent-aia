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
