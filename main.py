from core.orchestrator import BSPPipeline


def main():

    pipeline = BSPPipeline(
        "datasets/complex"
    )

    contexts = pipeline.run()

    print("\n")
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)

    # for context in contexts:

    #     print(f"File : {context.bundle.filename}")

    #     print(
    #         f"Candidate : {context.candidate.candidate_type.value}"
    #     )

    #     print("-" * 60)
    for context in contexts:

        print("=" * 80)

        print(context.bundle.filename)

        print("=" * 80)

        print("Candidate")

        print(context.candidate.candidate_type.value)

        print()

        print("Engineer")

        print(context.engineer.summary)

        print()

        print("Recommendation")

        print(context.engineer.recommendation)

        print()

        print("Risk")

        print(context.engineer.risk)

        print()

        print("Confidence")

        print(context.engineer.confidence)

    print()

    print(f"Total Files : {len(contexts)}")


if __name__ == "__main__":
    main()