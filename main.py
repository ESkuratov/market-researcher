#!/usr/bin/env python3
import sys

from dotenv import load_dotenv

from agent import run_agent


def main():
    load_dotenv()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = sys.stdin.readline().strip()

    if not query:
        print("Ошибка: запрос не может быть пустым.")
        sys.exit(1)

    report = run_agent(query)
    print(report)


if __name__ == "__main__":
    main()
