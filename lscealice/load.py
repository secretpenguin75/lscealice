from .dic import Tiepoint, load_dic_file


def unzip_tiepoints(tiepoints: dict[str, list[Tiepoint]]):
    # converts a tiepoints dic with lists of tiepoints
    # to two dictionaries with sorted tiepoints as array

    xp1_dic: dict[str, list[float]] = {}
    xp2_dic: dict[str, list[float]] = {}

    for profile_key, tiepointlist in tiepoints.items():
        xp = [(bob["profile_depth"], bob["ref_depth"]) for bob in tiepointlist]

        if not xp:
            continue

        # sort points
        xp1, xp2 = zip(*sorted(xp))

        xp1_dic[profile_key] = xp1
        xp2_dic[profile_key] = xp2

    return xp1_dic, xp2_dic


def load_marked_points(aligfile: str):
    # convert the tiepoints stored in the dictionary to the xp1 and xp2 lists

    new_dic = load_dic_file(aligfile)

    return unzip_tiepoints(new_dic["tiepoints"])


def load_profiles_data(aligfile: str):
    full_dic = load_dic_file(aligfile)

    cores_dic = {key: value for key, value in full_dic["cores"].items() if key != "REF"}
    ref_dic = full_dic["cores"]["REF"]

    return ref_dic, cores_dic


def load_profiles_metadata(aligfile: str):
    full_dic = load_dic_file(aligfile)

    cores_dic = {
        key: value for key, value in full_dic["metadata"].items() if key != "REF"
    }
    ref_dic = full_dic["metadata"]["REF"]

    return ref_dic, cores_dic
