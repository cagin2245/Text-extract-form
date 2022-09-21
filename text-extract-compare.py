
from difflib import SequenceMatcher

def string_comparison(list1,list2): # -> Jaccard Similarity
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1)+ len(list2)) - intersection
    return float(intersection) / union
    
def is_string_similar(s1: str,s2: str, treshold: float = 0.48): # String karşılaştırması 
    seq = SequenceMatcher(None,s1,s2)
    # print(seq.ratio()*100) -> Karşılaştırma yüzdelik oranının yazdırılması
    return SequenceMatcher(None,s1,s2).ratio() >= treshold