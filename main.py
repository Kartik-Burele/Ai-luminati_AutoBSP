from core.orchestrator import BSPPipeline
import pathlib


def main():

    project_root = pathlib.Path(__file__).resolve().parent
    pipeline = BSPPipeline(
        str(project_root / "datasets" / "complex")
    )




    contexts = pipeline.run()

    print("\n")
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)

    for context in contexts:

        print("=" * 80)
        print(f"File: {context.bundle.filename}")
        print("=" * 80)

        print(f"Candidate Mode: {context.candidate.candidate_type.value}\n")

        print("--- Engineer Agent ---")
        if context.engineer:
            print(f"Summary: {context.engineer.summary}")
            print(f"Recommendation: {context.engineer.recommendation}")
            print(f"Risk: {context.engineer.risk}")
            print(f"Confidence: {context.engineer.confidence}%")
        else:
            print("No engineering report.")
        print()

        print("--- Reviewer Agent ---")
        if context.reviewer:
            print(f"Validation: {context.reviewer.validation}")
            print(f"Risk Assessment: {context.reviewer.risk}")
            print(f"Reviewer Confidence: {context.reviewer.confidence}%")
        else:
            print("No reviewer report.")
        print()

        print("--- Manager (PM) Agent ---")
        if context.manager:
            print(f"Effort Grade: {context.manager.effort}")
            print(f"Priority: {context.manager.priority}")
            print(f"Business Impact: {context.manager.business_impact}")
            print(f"Estimated Dev-Hours: {context.manager.estimated_hours} hours")
        else:
            print("No manager report.")
        print()

    print()
    print(f"Total Files Processed: {len(contexts)}")


if __name__ == "__main__":
    main()