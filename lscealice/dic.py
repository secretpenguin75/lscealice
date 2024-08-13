from typing import Any, TypedDict, cast, Iterable
from pickle import dump, load

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from .excel import read

Entry = Any  # TODO


class Cores(TypedDict):
    data: NDArray[np.float64]
    depth: NDArray[np.float64]


class Tiepoint(TypedDict):
    profile_depth: float
    ref_depth: float
    species: str


class Dic(TypedDict):
    cores: dict[str, dict[str, Cores]]
    metadata: Entry
    tiepoints: dict[str, list[Tiepoint]]


def load_dic_file(filename: str):
    with open(filename, "rb") as fp:
        return cast(Dic, load(fp))


def write_dic_file(dic: Dic, filename: str):
    with open(filename, "wb") as fp:
        dump(dic, fp)


def initAlignmentFile(
    datafiles: Iterable[str],
    metadatafiles: Iterable[str],
    ref_lab: str,
    min_depth: float,
    max_depth: float,
):
    new_dic = Dic(
        cores={},
        metadata={},
        tiepoints={},
    )

    for datafile in datafiles:
        xls = pd.ExcelFile(datafile)
        core_names = map(str, xls.sheet_names[:])
        for i, lab in enumerate(core_names):
            df = read(datafile, i)
            dfnp = df.to_numpy()  # type: ignore
            ## todo later: adjust the code for then sample_date is not defined
            # sample_date = datetime.date(2000,1,1) # just a random date for now

            core_depth = dfnp[1:, 0].astype(None)

            if lab not in new_dic["tiepoints"].keys():
                # initialize tiepoints with empty lists
                new_dic["tiepoints"][lab] = []

            if lab not in new_dic["cores"].keys():
                new_dic["cores"][lab] = {}

            for i in range(1, len(df.T)):
                chem_name: str = dfnp[0, i]
                chem_profile = dfnp[1:, i].astype(None)

                # for Agnese in july 2024: restrict to the first 18 meters
                ind = np.logical_and(core_depth > min_depth, core_depth < max_depth)

                new_dic["cores"][lab][chem_name] = Cores(
                    data=chem_profile[ind].copy(),
                    depth=core_depth[ind].copy(),
                )

    for datafile in metadatafiles:
        xls = pd.ExcelFile(datafile)
        core_names = map(str, xls.sheet_names[:])
        for i, lab in enumerate(core_names):
            df = read(datafile, i)
            if lab not in new_dic["metadata"].keys():
                # initialize tiepoints with empty lists
                new_dic["metadata"][lab] = {}
            for i in range(0, len(df.T)):
                # metadata_name = df.to_numpy()[0,i]
                metadata_name = df.iloc[0, i]

                # metadata_value = df.to_numpy()[1,i]
                metadata_value = df.iloc[1, i]

                new_dic["metadata"][lab][metadata_name] = metadata_value

    new_dic["cores"]["REF"] = new_dic["cores"][ref_lab].copy()

    if ref_lab in new_dic["metadata"].keys():
        new_dic["metadata"]["REF"] = new_dic["metadata"][ref_lab].copy()

    return new_dic
