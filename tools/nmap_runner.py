# tools/nmap_runner.py

import paramiko
import os
import re

from dotenv import load_dotenv

load_dotenv()

def run_nmap(target: str, options: list[str]) -> str:
    """
    Executes Nmap on remote Kali machine with safe options.
    """
    host = os.environ["KALI_HOST"]
    user = os.environ["KALI_USER"]
    key_file = os.environ["KALI_SSH_KEY"]

    allowed_flags = {"-T4", "-F", "-O", "-sV", "--sC", "-sU", "-p-", "-Pn", "-n"}

    def is_safe_option(opt: str) -> bool:
        return opt in allowed_flags or re.fullmatch(r"-p\d{1,5}(-\d{1,5})?", opt)

    safe_opts = [opt for opt in options if is_safe_option(opt)]
    command = f"nmap {' '.join(safe_opts)} {target}"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, key_filename=key_file)

    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    ssh.close()

    if error:
        raise RuntimeError(f"Error running nmap: {error}")
    return output