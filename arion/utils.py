from typing import List, Dict
from sortedcontainers import SortedList
import glob
import pandas as pd


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
    def __init__(self, peak_list: List[MetabolitePeak], metabolite_sizes: Dict[str, int]):
        self._peaks = SortedList(peak_list)
        self._peak_lengths = metabolite_sizes

    @property
    def metabolite_peak_size(self):
        return self._peak_lengths

    def query(self, qu: List[float], tolerance=0.015):
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
            jaccard_score = overlap / self._peak_lengths[met_id]
            metabolite_list.append({
                "metabolite_id": met_id,
                "score": jaccard_score,
                "overlap": overlap
            })

        return sorted(metabolite_list, key=lambda i: i['score'], reverse=True)

    def full_query(self, query: List[float], tolerance=0.015):
        acceptable_mets = {i['metabolite_id'] for i in self.query(query, tolerance) if i['score'] >= 0.5}

        result = []
        for q in query:
            lower = MetabolitePeak(None, q - tolerance, None)
            upper = MetabolitePeak(None, q + tolerance, None)

            result.append([p for p in self._peaks.irange(lower, upper) if p.metabolite_id in acceptable_mets])

        return result


def generate_db():
    data_dir = '/media/shared/arion_data/metabolites'
    peak_file = 'simulation_1/peaks/sim_600MHz_peaks_standard.csv'
    cutoff = 0.001

    peaks = []
    peak_sizes = {}
    for met_idx, d in enumerate(glob.glob(f'{data_dir}/bmse*')):
        metabolite_id = d.split('/')[-1]
        peak_df = pd.read_csv(f'{d}/{peak_file}')

        peak_length = 0
        for idx, peak in peak_df.iterrows():
            if peak['Amp'] >= cutoff:
                peaks.append(MetabolitePeak(metabolite_id, peak['PPM'], peak['Amp']))
                peak_length += 1

        peak_sizes[metabolite_id] = peak_length

    print(f'found {len(peaks)} peaks across {met_idx + 1} metabolites')
    return PeakDB(peaks, peak_sizes)
