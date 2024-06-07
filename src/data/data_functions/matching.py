import h5py
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

from .hdf5_utils import save_hdf5


# ========================================================================================================================
#           Matching functions
# ========================================================================================================================

def match_data() -> None:
    """
    Match the AutoPi data with the reference data (ARAN and P79) and the GoPro data into segments
    """

    # Define path to segment files
    segment_file = 'data/interim/gm/segments.hdf5'

    # Load reference and GoPro data
    aran = {
        'hh': pd.read_csv('data/raw/ref_data/cph1_aran_hh.csv', sep=';', encoding='unicode_escape').fillna(0),
        'vh': pd.read_csv('data/raw/ref_data/cph1_aran_vh.csv', sep=';', encoding='unicode_escape').fillna(0)
    }

    p79 = {
        'hh': pd.read_csv('data/raw/ref_data/cph1_zp_hh.csv', sep=';', encoding='unicode_escape'),
        'vh': pd.read_csv('data/raw/ref_data/cph1_zp_vh.csv', sep=';', encoding='unicode_escape')
    }
    
    gopro_data = {}
    car_trips = ["16011", "16009", "16006"]
    for trip_id in car_trips:
        gopro_data[trip_id] = {}
        for measurement in ['gps5', 'accl', 'gyro']:
            gopro_data[trip_id][measurement] = pd.read_csv(f'data/interim/gopro/{trip_id}/{measurement}.csv')

    # Create folders for saving
    Path('data/interim/aran').mkdir(parents=True, exist_ok=True)
    Path('data/interim/p79').mkdir(parents=True, exist_ok=True)
    Path('data/interim/gopro').mkdir(parents=True, exist_ok=True)

    # Remove old segment files if they exist
    for folder in ['aran', 'p79', 'gopro']:
        segment_path = Path(f'data/interim/{folder}/segments.hdf5')
        if segment_path.exists():
            segment_path.unlink()

    # Match data
    with h5py.File(segment_file, 'r') as f:
        segment_files = [f[str(i)] for i in range(len(f))]
        pbar = tqdm(segment_files)
        for i, segment in enumerate(pbar):
            pbar.set_description(f"Matching segment {i+1:03d}/{len(segment_files)}")

            direction = segment['direction'][()].decode("utf-8")
            trip_name = segment["trip_name"][()].decode('utf-8')
            pass_name = segment["pass_name"][()].decode('utf-8')

            segment_lonlat = segment['measurements']['gps'][()][:, 2:0:-1]

            aran_dir = aran[direction]
            p79_dir = p79[direction]

            # Match to ARAN data
            aran_match = find_best_start_and_end_indeces_by_lonlat(aran_dir[["Lon", "Lat"]].values, segment_lonlat)
            aran_segment = cut_dataframe_by_indeces(aran_dir, *aran_match)
            save_hdf5(aran_segment, 'data/interim/aran/segments.hdf5', segment_id=i)

            # Match to P79 data
            p79_match = find_best_start_and_end_indeces_by_lonlat(p79_dir[["Lon", "Lat"]].values, segment_lonlat)
            p79_segment = cut_dataframe_by_indeces(p79_dir, *p79_match)
            save_hdf5(p79_segment, 'data/interim/p79/segments.hdf5', segment_id=i)
                
            # gopro is a little different.. (These trips do not have any corresponding gopro data, so we skip them)
            if trip_name not in ["16006", "16009", "16011"]:
                continue
            
            gopro_segment = {}
            for measurement in ['gps5', 'accl', 'gyro']:
                start_index, end_index, start_diff, end_diff = find_best_start_and_end_indeces_by_time(segment, gopro_data[trip_name][measurement]["date"])

                if max(start_diff, end_diff) > 1:
                    continue
                
                gopro_segment[measurement] = gopro_data[trip_name][measurement][start_index:end_index].to_dict('series')

            if gopro_segment != {}:
                save_hdf5(gopro_segment, 'data/interim/gopro/segments.hdf5', segment_id=i)


def find_best_start_and_end_indeces_by_lonlat(trip: np.ndarray, section: np.ndarray) -> tuple[int, int]:
    """
    Find the start and end indeces of the section data that are closest to the trip data

    Parameters
    ----------
    trip : np.ndarray
        The longitudal and lattitudal coordinates of the trip data
    section : np.ndarray
        The longitudal and lattitudal coordinates of the section
    """

    # Find the start and end indeces of the section data that are closest to the trip data
    lon_a, lat_a = trip[:,0], trip[:,1]
    lon_b, lat_b = section[:,0], section[:,1]
    
    start_index = np.argmin(np.linalg.norm(np.column_stack((lon_a, lat_a)) - np.array([lon_b[0], lat_b[0]]), axis=1))
    end_index = np.argmin(np.linalg.norm(np.column_stack((lon_a, lat_a)) - np.array([lon_b[-1], lat_b[-1]]), axis=1))

    return start_index, end_index+1


def find_best_start_and_end_indeces_by_time(current_segment: h5py.Group, gopro_time: np.ndarray) -> tuple[int, int, float, float]:
    """
    Find the start and end indeces of the section data based on time

    Parameters
    ----------
    current_segment : h5py.Group
        The current segment data
    gopro_time : np.ndarray
        The time data from the GoPro
    """

    # Find the start and end indeces of the section data based on time
    current_segment_start_time = current_segment["measurements"]["gps"][()][0, 0]
    current_segment_end_time = current_segment["measurements"]["gps"][()][-1, 0]
    segment_time = [current_segment_start_time, current_segment_end_time]
    
    diff_start = (gopro_time - segment_time[0]).abs()
    start_index = diff_start.idxmin()
    start_diff = diff_start.min()
    
    diff_end = (gopro_time - segment_time[1]).abs()
    end_index = diff_end.idxmin()
    end_diff = diff_end.min()

    return start_index, end_index, start_diff, end_diff


def cut_dataframe_by_indeces(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    return df.iloc[start:end]