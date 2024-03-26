# services/keyword_count.py
def count_keywords(text, keywords):
    result_data = []
    for keyword in keywords:
        count = text.lower().count(keyword.lower())
        result_data.append({"keyword": keyword, "count": count})
    return result_data
