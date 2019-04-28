import logging
import pandas as pd
import networkx as nx
import numpy as np
import json

from arion.utils import generate_db, peakset2ppm

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("grid_search.py")

data_dir = '/media/shared/arion_data/metabolites'

filled = pd.read_csv('../data/speaq_results/filled.csv').iloc[:, 1:]
features = pd.read_csv('../data/speaq_results/features.csv').iloc[:, 1:]

MAX_CLIQUES = 100000
PEARSON_CORRELATION_THRESHOLDS = np.arange(.5, .95, .05)
MINIMUM_PERCENTAGE_OF_PEAKS_MATCHED_THRESHOLDS = np.arange(.3, .9, .1)

results = []
peak_db = generate_db(data_dir)
for pearson_thresh in PEARSON_CORRELATION_THRESHOLDS:

    corr_mat = features.corr('spearman')

    g = nx.Graph(corr_mat > pearson_thresh)
    cliqs = []

    for idx, cliq in enumerate(nx.find_cliques(g)):
        if idx > MAX_CLIQUES:
            raise Exception(f"More than {MAX_CLIQUES} cliques found")

        cliqs.append(cliq)
    logger.info(f"pearson_thresh: {pearson_thresh:.2f} -- identified {len(cliqs)} cliques")

    for missing_thresh in MINIMUM_PERCENTAGE_OF_PEAKS_MATCHED_THRESHOLDS:
        found = False
        identified_metabolites = {}
        for idx, cliq in enumerate(cliqs):
            res = peak_db.query_n(peakset2ppm(cliq, filled), missing_thresh=missing_thresh)
            for qs in res:
                if qs['score'] >= 0.1 and len(
                        peak_db.metabolite_peaks[qs['metabolite_id']]) > 1 and len(qs['missing']) < 2:
                    if qs['metabolite_id'] not in identified_metabolites:
                        identified_metabolites[qs['metabolite_id']] = []

                    identified_metabolites[qs['metabolite_id']].append({
                        "id": idx,
                        "cliq": cliq,
                        "query_results": qs
                    })

        logger.info(
            f"pearson_thresh: {pearson_thresh:.2f}, match_thresh: {missing_thresh:.2f} "
            f"-- identified {len(list(identified_metabolites.keys()))} metabolites")

        max_scored_metabolites = []
        for met_id in identified_metabolites.keys():
            metabolite_max_score = max(identified_metabolites[met_id], key=lambda m: m['query_results']['score'])

            max_scored_metabolites.append(metabolite_max_score)

        results.append({
            'pearson_thresh': pearson_thresh,
            'match_thresh': missing_thresh,
            'sorted_metabolites': sorted(max_scored_metabolites, key=lambda m: -m['query_results']['score'])
        })

        with open("../data/grid_search_results.json", 'w') as f:
            json.dump(results, f)
