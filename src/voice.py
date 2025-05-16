from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np


encoder = VoiceEncoder(device='cpu')

def reference_embedding(references_paths):
    embeds = []
    for path in references_paths:
        wav = preprocess_wav(path)
        emb = encoder.embed_utterance(wav)
        embeds.append(emb)
    
    avg = np.mean(embeds, axis=0)
    avg /= np.linalg.norm(avg)
    return avg


def preprocess(path):
    wav = preprocess_wav(path)
    emb = encoder.embed_utterance(wav)
    emb /= np.linalg.norm(emb)
    return emb


def voice_verify(references_paths, test_path, verification_threshold=0.8) -> tuple[bool, float]:
    ref = reference_embedding(references_paths)
    test= preprocess(test_path)
    similarity = np.dot(ref, test)

    return True if similarity >= verification_threshold else False, similarity




