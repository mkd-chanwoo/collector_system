from better_profanity import profanity
from detoxify import Detoxify
import random


class ToxicFilter:
    def __init__(self, sample_rate=0.05, max_length=512):
        profanity.load_censor_words()

        self.model = Detoxify("original")

        self.sample_rate = sample_rate   # 5%만 검사
        self.max_length = max_length     # 길이 제한


    def badword_filter(self, text):

        return profanity.contains_profanity(text)


    def toxicity_filter(self, text, threshold=0.9):

        # 1. 샘플링 
        if random.random() > self.sample_rate:
            return False, 0.0

        # 2. 길이 제한
        text = text[:self.max_length]

        # 3. 모델 실행
        score = self.model.predict(text)
        toxicity_score = score["toxicity"]

        return toxicity_score > threshold, toxicity_score