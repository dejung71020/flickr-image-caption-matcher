# src/application/dataset_service.py
import random
import time
from src.domain.entities import Sample
from src.domain.value_objects import MismatchType, Label
from src.infrastructure.flickr_repository import FlickrRepository
from src.infrastructure.gemini_client import GeminiClient


class DatasetService:
    def __init__(self, repo: FlickrRepository, gemini: GeminiClient):
        self.repo = repo
        self.gemini = gemini

    def build(self) -> list[Sample]:
        all_ids = self.repo.sample_image_ids(120, seed=42)
        samples = []

        original_ids = all_ids[:40]
        shuffle_ids  = all_ids[40:60]
        object_ids   = all_ids[60:80]
        action_ids   = all_ids[80:100]
        place_ids    = all_ids[100:]

        for image_id in original_ids:
            caption = self.repo.get_captions(image_id)[0]
            samples.append(Sample(
                image_id=image_id,
                image_path=self.repo.get_image_path(image_id),
                caption=caption,
                label=Label.MATCH,
                mismatch_type=MismatchType.ORIGINAL,
            ))

        for image_id in shuffle_ids:
            caption = self.repo.get_random_caption_from_other(image_id)
            samples.append(Sample(
                image_id=image_id,
                image_path=self.repo.get_image_path(image_id),
                caption=caption,
                label=Label.MISMATCH,
                mismatch_type=MismatchType.SHUFFLE,
            ))

        for ids_list, mtype in [
            (object_ids, MismatchType.OBJECT_SWAP),
            (action_ids, MismatchType.ACTION_SWAP),
            (place_ids,  MismatchType.PLACE_SWAP),
        ]:
            for i, image_id in enumerate(ids_list):
                original_caption = self.repo.get_captions(image_id)[0]
                print(f"  swap 생성 중 [{mtype.value}] {i+1}/20")
                swapped = self.gemini.generate_swap(original_caption, mtype.value)
                samples.append(Sample(
                    image_id=image_id,
                    image_path=self.repo.get_image_path(image_id),
                    caption=swapped,
                    label=Label.MISMATCH,
                    mismatch_type=mtype,
                ))

        return samples