import time, json, random
from parse_xml import parse_sms_xml
import os
def linear_search(transactions, target_id):
    for t in transactions:
        if t['Id'] == target_id:
            return t
    return None

def dict_lookup(index, target_id):
    return index.get(target_id)

def build_index(transactions):
    return {t['Id']: t for t in transactions}

def measure(transactions, trials=1000, sample_ids=None):
    if sample_ids is None:
        sample_ids = [random.choice(transactions)['Id'] for _ in range(20)]
    index = build_index(transactions)

    
    # Linear search timing
    start = time.perf_counter()
    for sid in sample_ids:
        linear_search(transactions, sid)
    linear_time = time.perf_counter() - start


    # Dict lookup timing
    start = time.perf_counter()
    for sid in sample_ids:
        dict_lookup(index, sid)
    dict_time = time.perf_counter() - start
    return linear_time, dict_time, sample_ids

if __name__ == '__main__':
    transactions = parse_sms_xml(os.path.join(os.path.dirname(__file__), "modified_sms_sample.xml"))

    
    sample_ids = [t['Id'] for t in transactions[:20]]

    linear_time, dict_time, sample_ids = measure(transactions, sample_ids=sample_ids)

    print('Records:', len(transactions))
    print('Sample IDs:', sample_ids)
    print(f'Linear search total time for {len(sample_ids)} searches: {linear_time:.6f} sec')
    print(f'Dict lookup total time for {len(sample_ids)} searches: {dict_time:.6f} sec')
    print('Dict lookup is faster by factor:', linear_time/dict_time if dict_time>0 else 'inf')
