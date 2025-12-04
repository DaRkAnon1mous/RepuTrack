# backend/nlp/fake_detector.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import pickle
import re
import os

# Load DistilBERT
distilbert_tokenizer = AutoTokenizer.from_pretrained(r"D:\Coding Workspaces\RepuTrack\backend\nlp\distilbert_fake_review")
distilbert_model = AutoModelForSequenceClassification.from_pretrained(r"D:\Coding Workspaces\RepuTrack\backend\nlp\distilbert_fake_review")
distilbert_model.eval()

# Load BiLSTM
class BiLSTM(torch.nn.Module):
    def __init__(self, embedding_matrix, hidden_dim=128, num_layers=2):
        super().__init__()
        self.embedding = torch.nn.Embedding.from_pretrained(torch.FloatTensor(embedding_matrix), padding_idx=0)
        self.lstm = torch.nn.LSTM(300, hidden_dim, num_layers, bidirectional=True, batch_first=True, dropout=0.5)
        self.fc = torch.nn.Linear(hidden_dim * 2, 2)
        self.dropout = torch.nn.Dropout(0.5)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        out = self.dropout(lstm_out[:, -1, :])
        return self.fc(out)

# Load embedding matrix & word_to_idx
embedding_matrix = np.load(r"D:\Coding Workspaces\RepuTrack\backend\nlp\embedding_matrix.npy")
with open(r"D:\Coding Workspaces\RepuTrack\backend\nlp\word_to_idx.pkl", "rb") as f:
    word_to_idx = pickle.load(f)

bilstm_model = BiLSTM(embedding_matrix)
bilstm_model.load_state_dict(torch.load(r"D:\Coding Workspaces\RepuTrack\backend\nlp\bilstm_fake_review.pth", map_location="cpu"))
bilstm_model.eval()

def predict_fake_ensemble(reviews):
    if not reviews:
        return reviews, 0.0

    texts = [re.sub(r'[^a-z\s]', '', r["text"].lower()) for r in reviews]

    # DistilBERT
    inputs = distilbert_tokenizer(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        d_outputs = distilbert_model(**inputs)
        d_probs = torch.softmax(d_outputs.logits, dim=1)[:, 1].numpy()

    # BiLSTM
    indices = []
    for text in texts:
        words = text.split()[:100]
        idxs = [word_to_idx.get(w, 1) for w in words] + [0] * (100 - len(words))
        indices.append(idxs)
    indices = torch.tensor(indices)
    with torch.no_grad():
        b_outputs = bilstm_model(indices)
        b_probs = torch.softmax(b_outputs, dim=1)[:, 1].numpy()

    # Ensemble
    final_probs = (d_probs + b_probs) / 2
    fake_count = 0
    for i, prob in enumerate(final_probs):
        is_fake = prob > 0.5
        reviews[i]["is_fake"] = bool(is_fake)
        reviews[i]["fake_probability"] = round(float(prob), 3)
        if is_fake:
            fake_count += 1

    fake_ratio = round(fake_count / len(reviews), 3)
    return reviews, fake_ratio