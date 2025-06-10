from torch import argmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.nn.functional import softmax
import pandas as pd

tokenizer = AutoTokenizer.from_pretrained("launch/POLITICS")
model = AutoModelForSequenceClassification.from_pretrained("matous-volf/political-leaning-politics")

def example_eval():
    text = "The government should cut taxes because it is not using them efficiently anyway."

    tokens = tokenizer(text, return_tensors="pt")
    output = model(**tokens)
    logits = output.logits

    political_leaning = argmax(logits, dim=1).item()
    probabilities = softmax(logits, dim=1)
    score = probabilities[0, political_leaning].item()
    print(political_leaning, score)
    
def batch_eval(texts):
    tokens = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    output = model(**tokens)
    logits = output.logits

    political_leanings = argmax(logits, dim=1)
    probabilities = softmax(logits, dim=1)
    scores = probabilities[range(len(texts)), political_leanings].tolist()
    
    
    leanings = ["Left", "Center", "Right"]

    for text, leaning, score in zip(texts, political_leanings.tolist(), scores):
        print(f"Text: {text}\nPredicted leaning: {leanings[leaning]}, Score: {score}\n")
    
def test_data_eval():
    left_wing_statements = [
        "Healthcare is a human right and should be accessible to everyone.",
        "We need to raise the minimum wage to ensure a living wage for all workers.",
        "Climate change is an urgent crisis and requires bold government action.",
        "We must reform the criminal justice system to end systemic racism.",
        "Billionaires should pay their fair share in taxes.",
        "Education should be free and accessible to all, from preschool through college.",
        "We need stronger protections for workers and unions.",
        "Immigrants make our country stronger and deserve humane treatment.",
        "Everyone deserves affordable housing and basic social services.",
        "Corporations should be held accountable for exploiting people and the planet."
    ]
    
    right_wing_statements = [
        "Lower taxes and less government regulation lead to a stronger economy.",
        "The Second Amendment protects our right to bear arms and must be upheld.",
        "Illegal immigration undermines the rule of law and national sovereignty.",
        "Traditional family values are the foundation of a stable society.",
        "School choice and charter schools give parents better educational options.",
        "The free market is the best way to drive innovation and prosperity.",
        "Strong national defense is essential to protect our freedoms.",
        "Abortion should be restricted to protect the rights of the unborn.",
        "Government spending needs to be reduced to avoid national debt.",
        "Patriotism and respect for the flag are important American values."
    ]
    
    batch_eval(left_wing_statements + right_wing_statements)
    
if __name__ == "__main__":
    test_data_eval()
