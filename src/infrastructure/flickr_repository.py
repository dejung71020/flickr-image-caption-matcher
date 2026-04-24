# src/infrastructure/flickr_repository.py
import pandas as pd
import random
from pathlib import Path

class FlickrRepository:
    def __init__(self, caption_file: str, image_dir: str):
        self.image_dir = Path(image_dir)
        self.df = pd.read_csv(caption_file)
        self.df.columns = ['image_id', 'caption']

    def get_all_image_ids(self) -> list[str]:
        return self.df['image_id'].unique().tolist()
    
    def get_captions(self, image_id: str) -> list[str]:
        return self.df[self.df['image_id']==image_id]['caption'].tolist()
    
    def get_image_path(self, image_id: str) -> str:
        return str(self.image_dir / image_id)
    
    def get_random_caption_from_other(self, exclude_id: str) -> str:
        other = self.df[self.df['image_id'] != exclude_id]
        row = other.sample(1).iloc[0]
        return row['caption']
    
    def sample_image_ids(self, n: int, seed: int = 42) -> list[str]:
        random.seed(seed)
        ids = self.get_all_image_ids()
        return random.sample(ids, n)