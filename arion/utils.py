from typing import List, Dict
from sortedcontainers import SortedList
import glob
import pandas as pd
import networkx as nx


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def color(string, c):
        return c + string + Colors.ENDC


class MetabolitePeak:
    def __init__(self, metabolite_id, ppm, amp):
        self.id = f'{metabolite_id}_{ppm:.5f}'
        self.metabolite_id = metabolite_id
        self.ppm = ppm
        self.amp = amp

    def __eq__(self, other):
        return self.ppm == other.ppm

    def __lt__(self, other):
        return self.ppm < other.ppm

    def __str__(self):
        return f'<Peak id:{self.id} metabolite_id:{self.metabolite_id} ppm:{self.ppm:.5f} amplitude:{self.amp:.5f}>'

    def __repr__(self):
        return self.__str__()


class PeakDB:
    def __init__(self, peak_list: List[MetabolitePeak]):
        self._peaks = SortedList(peak_list)

        self.peak_dict = {p.id: p for p in peak_list}

        metabolite_peaks = {}
        for peak in peak_list:
            if peak.metabolite_id not in metabolite_peaks:
                metabolite_peaks[peak.metabolite_id] = []

            metabolite_peaks[peak.metabolite_id].append(peak)

        self._metabolite_peaks = metabolite_peaks

    @property
    def metabolite_peaks(self) -> Dict[str, List[MetabolitePeak]]:
        return self._metabolite_peaks

    def query_n(self, qu: List[float], tolerance=0.0075):
        graphs = {}
        for q in qu:
            lower = MetabolitePeak(None, q - tolerance, None)
            upper = MetabolitePeak(None, q + tolerance, None)

            for retrieved_peak in self._peaks.irange(lower, upper):
                if retrieved_peak.metabolite_id not in graphs:
                    graphs[retrieved_peak.metabolite_id] = nx.Graph()

                graphs[retrieved_peak.metabolite_id].add_edge(f'l_{q:.5f}', retrieved_peak.id)

        result_map = []
        for met, graph in graphs.items():
            result = {
                'metabolite_id': met,
                'matches': {}
            }

            for i in nx.components.connected_components(graph):
                matching = nx.bipartite.maximum_matching(graph.subgraph(i))
                result['matches'].update({k: v for k, v in matching.items() if k.startswith("l_")})

            result['score'] = len(result['matches']) / len(self.metabolite_peaks[met])

            result['missing'] = []
            matched_peaks = [self.peak_dict[peak_id] for peak_id in result['matches'].values()]
            for peak in self.metabolite_peaks[met]:
                if peak not in matched_peaks and any([peak.amp >= p.amp for p in matched_peaks]):
                    result['missing'].append(peak.id)

            result_map.append(result)

        return result_map

    def query(self, qu: List[float], tolerance=0.0075):
        result_map = {}
        for q in qu:
            matched = set()
            lower = MetabolitePeak(None, q - tolerance, None)
            upper = MetabolitePeak(None, q + tolerance, None)

            for retrieved_peak in self._peaks.irange(lower, upper):
                if retrieved_peak.metabolite_id not in result_map:
                    result_map[retrieved_peak.metabolite_id] = 0

                if retrieved_peak.metabolite_id not in matched:
                    matched.add(retrieved_peak.metabolite_id)
                    result_map[retrieved_peak.metabolite_id] += 1

        metabolite_list = []
        for met_id, overlap in result_map.items():
            jaccard_score = overlap / len(self.metabolite_peaks[met_id])
            metabolite_list.append({
                "metabolite_id": met_id,
                "score": jaccard_score,
                "overlap": overlap
            })

        return sorted(metabolite_list, key=lambda i: i['score'], reverse=True)


def peakset2ppm(peakset, filled):
    return [filled.loc[filled.peakIndex == int(vtx), :].peakPPM.mean() for vtx in peakset]


def generate_db(data_dir):
    peak_file = 'simulation_1/peaks/sim_600MHz_peaks_standard.csv'
    cutoff = 0.001

    peaks = []
    met_idx = 0
    for met_idx, d in enumerate(glob.glob(f'{data_dir}/bmse*')):
        metabolite_id = d.split('/')[-1]
        peak_df = pd.read_csv(f'{d}/{peak_file}')

        for idx, peak in peak_df.iterrows():
            if peak['Amp'] >= cutoff:
                peaks.append(MetabolitePeak(metabolite_id, peak['PPM'], peak['Amp']))

    print(f'found {len(peaks)} peaks across {met_idx + 1} metabolites')
    return PeakDB(peaks)
