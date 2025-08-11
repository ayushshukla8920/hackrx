import subprocess
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
async def handle_agentic_workflow(document_url: str, question: str):
    try:
        script_dir = Path(__file__).parent.resolve()
        services_dir = script_dir.parent / 'tools'
        command = ["node", "agent.js", document_url, question]
        logger.info(f"--- Python Caller: Running agent from '{services_dir}' ---")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            cwd=services_dir
        )
        final_answer = result.stdout.strip()
        logger.info("--- Python Caller: Node.js Agent Finished ---")
        return final_answer
    except subprocess.CalledProcessError as e:
        logger.error("--- Python Caller: The Node.js agent exited with an error ---", file=sys.stderr)
        logger.error(f"Exit Code: {e.returncode}", file=sys.stderr)
        logger.error("\n--- Agent's Standard Output ---", file=sys.stderr)
        logger.error(e.stdout, file=sys.stderr)
        logger.error("\n--- Agent's Standard Error ---", file=sys.stderr)
        logger.error(e.stderr, file=sys.stderr)
        return None
    except FileNotFoundError:
        logger.error(f"Error: 'node' command not found or script 'agent.js' not found in '{services_dir}'.", file=sys.stderr)
        return None