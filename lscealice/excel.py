import pandas as pd
import numpy as np


def read(io: str, sheet_name: int):
    df = pd.read_excel(  # type: ignore
        io, sheet_name=sheet_name, skiprows=0, header=None
    )

    return df.replace(  # type: ignore
        "n.a.", np.nan
    )
