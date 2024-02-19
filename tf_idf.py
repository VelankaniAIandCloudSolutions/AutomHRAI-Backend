from sklearn.feature_extraction.text import TfidfVectorizer

def do_tfidf(token):
    tfidf = TfidfVectorizer(max_df=0.05, min_df=0.002)
    words = tfidf.fit_transform(token)
    feature_names = tfidf.get_feature_names_out()
    sentence = " ".join(feature_names)
    return sentence
