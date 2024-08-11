from typing import Optional, Iterable

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from .load import load_profiles_data, load_marked_points
from .utils import depth_sqz_str


def load_alig_array(
    aligfile: str,
    species: str,
    vertical_scale: Optional[NDArray[np.float64]] = None,
    labels: Optional[Iterable[str]] = None,
):
    # create an array with

    ref_dic, cores_dic = load_profiles_data(aligfile)

    xp1_dic, xp2_dic = load_marked_points(aligfile)

    x: NDArray[np.float64] = (
        ref_dic[species]["depth"].copy() if vertical_scale is None else vertical_scale
    )

    if labels is None:
        labels = cores_dic.keys()

    # npits = len(labels)

    # data = chem_profiles[species]

    out = {}

    for profile in labels:
        if species in cores_dic[profile] and profile in xp1_dic.keys():
            xp = depth_sqz_str(
                cores_dic[profile][species]["depth"], xp1_dic[profile], xp2_dic[profile]
            )

            fp = cores_dic[profile][species]["data"]

            signal_new = np.interp(
                x,
                xp,
                fp,
                left=np.nan,
                right=np.nan,
            )

            out[profile] = signal_new

        else:
            print("missing data or tiepoints for ", profile)
            out[profile] = np.full(len(x), np.nan)

    return pd.DataFrame(data=out, index=x)
