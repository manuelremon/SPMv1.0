import argparse, json
from agent.agent import call_agent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-t", "--task", required=True, help="Tarea del agente")
    p.add_argument("--budget", type=int, default=2048, help="thinking budget tokens")
    args = p.parse_args()

    out = call_agent(args.task, budget=args.budget)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
