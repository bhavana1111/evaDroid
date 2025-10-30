from collections import Counter

class SharedMemory:
    def __init__(self):
        self.click_history=[]
        self.click_counter = Counter()
    
    def log_clickable(self,clickable):
        self.click_history.append(clickable)
        label = self.get_label(clickable)
        self.click_counter[label]+=1
    
    def get_recent_labels(self,n=10):
        return [
            self.get_label(c)
            for c in self.click_history[-n:]
            if self.get_label(c)
        ]
    def was_clicked(self,label):
        return self.click_counter[label]>0
    
    def get_duplicates(self):
        return [lbl for lbl,count in self.click_counter.items() if count>1]
    
    def get_unique_labels(self):
        return list(self.click_counter.keys())
    
    @staticmethod
    def get_label(clickable):
        return (
            clickable.get("text") or
            clickable.get("desc") or
            f'{clickable.get("class","")}-{clickable.get("res_id","")}'
        ).strip()
    
