"""
Main orchestration pipeline.

Pipeline:

Dataset
    ↓
Loader
    ↓
Diff Engine
    ↓
Comparator
    ↓
Pipeline Context
"""

from core.loader import DatasetLoader
from core.diff_engine import DiffEngine
from core.comparator import Comparator
from agents.engineer import EngineerAgent
from agents.reviewer import ReviewerAgent
from agents.manager import ManagerAgent

from models.pipeline_models import PipelineContext

from utils.debug import print_diff


class BSPPipeline:

    def __init__(self, dataset_path: str):

        self.loader = DatasetLoader(dataset_path)

        self.diff_engine = DiffEngine()

        self.comparator = Comparator()

        self.engineer = EngineerAgent()
        
        self.reviewer = ReviewerAgent()
        
        self.manager = ManagerAgent()

    def run(self):

        bundles = self.loader.load()

        contexts = []

        for bundle in bundles:

            diff = self.diff_engine.generate_diff(bundle)

            # Temporary debugging
            print_diff(diff)

            candidate = self.comparator.compare(diff)

            context = PipelineContext(
                bundle=bundle,
                diff=diff,
                candidate=candidate,
            )

            contexts.append(context)

        # Batch-process through agents in sequence
        contexts = self.engineer.analyze_batch(contexts)
        contexts = self.reviewer.analyze_batch(contexts)
        contexts = self.manager.analyze_batch(contexts)

        return contexts