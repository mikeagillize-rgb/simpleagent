from agent import agent

print("Assistente do Mike pronto. Digite 'sair' para encerrar.\n")

while True:
    pergunta = input("Você: ").strip()

    if not pergunta:
        continue

    if pergunta.lower() in ("sair", "exit", "quit"):
        print("Até mais, Vossa Excelência Mike! 👋")
        break

    result = agent.invoke(
        {"messages": [{"role": "user", "content": pergunta}]}
    )

    print(f"Assistente: {result['messages'][-1].text}\n")