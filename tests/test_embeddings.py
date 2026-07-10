from civisynth.embeddings import HashingEmbedder, cosine


def test_embedding_is_deterministic_and_normalized():
    emb = HashingEmbedder()
    v1 = emb.embed("the senate passed the tax bill")
    v2 = emb.embed("the senate passed the tax bill")
    assert v1 == v2
    assert abs(cosine(v1, v1) - 1.0) < 1e-9


def test_similar_texts_score_higher_than_unrelated():
    emb = HashingEmbedder()
    a = emb.embed("senate debates tax reform bill")
    b = emb.embed("tax reform bill discussed in the senate")
    c = emb.embed("wildfire season starts early in the west")
    assert cosine(a, b) > cosine(a, c)
