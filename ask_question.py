from backend.rag import RAGPipeline


print("\nInitializing AUTOSAR HLD Assistant...\n")

rag = RAGPipeline()

while True:

    question = input("\nEnter your question (or type 'exit'): ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    print("\nGenerating answer...\n")

    answer, sources = rag.answer_question(question)

    print("=" * 70)
    print("ANSWER")
    print("=" * 70)

    print(answer)

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in sources:
        print(
            f"- {source['source']} "
            f"(Page {source['page']})"
        )