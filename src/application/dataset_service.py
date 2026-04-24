# src/application/dataset_service.py
import re
import random
from src.domain.entities import Sample
from src.domain.value_objects import MismatchType, Label
from src.infrastructure.flickr_repository import FlickrRepository

# 일부로 객체 틀리게 바꾸려고 만듬
OBJECT_SWAPS = {
    "dog": "cat", "cat": "dog",
    "man": "woman", "woman": "man",
    "boy": "girl", "girl": "boy",
    "horse": "dog", "ball": "frisbee",
}

# 액션 틀리게 바꾸기 위한 딕셔너리
ACTION_SWAPS = {
    "running": "sleeping", "sleeping": "running",
    "jumping": "sitting", "sitting": "jumping",
    "playing": "eating", "eating": "playing",
    "swimming": "walking", "walking": "swimming",
    "riding": "pushing", "pushing": "riding",
    "climbing": "falling",
}

# 장소 틀리게 하기위한 딕셔너리
PLACE_SWAPS = {
    "grass": "water", "water": "grass",
    "beach": "mountain", "mountain": "beach",
    "street": "field", "field": "street",
    "pool": "grass", "sand": "snow", "snow": "sand",
}

# r'\b' 는 단어 경계이다. 단어가 아닌것을 확인
# r은 Raw String으로 \는 문장 그대로 받아들이게하는것
# pattern은 r'\bdog\b' 가 된다.
# replace는 단어 사이의 값이 들어가도 고치기 때문에 이 방식을 쓴다.
# re.IGNORECASE는 대소문자 구분을 하지 않는다.
def _swap_word(caption: str, swap_dict: dict) -> str | None:
    for original, replacement in swap_dict.items():
        pattern = r'\b' + original + r'\b'
        if re.search(pattern, caption, re.IGNORECASE):
            return re.sub(pattern, replacement, caption, count=1, flags=re.IGNORECASE)
    return None

class DatasetService:
    def __init__(self, repo: FlickrRepository):
        self.repo = repo

    def build(self) -> list[Sample]:
        all_ids = self.repo.sample_image_ids(120, seed=42)

        samples = []
        
        original_ids    = all_ids[:40]
        shuffle_ids     = all_ids[40: 60]
        object_ids      = all_ids[60: 80]
        action_ids      = all_ids[80: 100]
        place_ids       = all_ids[100:]

        for image_id in original_ids:
            # 해당 이미지에 존재하는 캡션이 5개정도인데 이것중에 가장 처음 꺼만 가져올게요.
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

        for image_id, swap_dict, mtype in [
            (object_ids, OBJECT_SWAPS, MismatchType.OBJECT_SWAP),
            (action_ids, ACTION_SWAPS, MismatchType.ACTION_SWAP),
            (place_ids, PLACE_SWAPS, MismatchType.PLACE_SWAP),
        ]:
            added = 0
            captions = []
            for img_id in image_id:
                captions += [(img_id, c) for c in self.repo.get_captions(img_id)]
            
            random.seed(42)
            random.shuffle(captions)

            for img_id, caption in captions:
                if added >= 20:
                    break
                swapped = _swap_word(caption, swap_dict)
                if swapped is None:
                    continue
                samples.append(Sample(
                    image_id=img_id,
                    image_path=self.repo.get_image_path(img_id),
                    caption=swapped,
                    label=Label.MISMATCH,
                    mismatch_type=mtype,
                ))
                added += 1
        return samples