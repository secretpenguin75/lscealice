from .dic import load_dic_file


def load_marked_points(aligfile: str):
    # convert the tiepoints stored in the dictionary to the xp1 and xp2 lists

    new_dic = load_dic_file(aligfile)

    xp1_dic: dict[str, list[float]] = {}
    xp2_dic: dict[str, list[float]] = {}

    for profile_key, tiepoints in new_dic["tiepoints"].items():
        xp = [(bob["profile_depth"], bob["ref_depth"]) for bob in tiepoints]

        if not xp:
            continue

        # sort points
        xp1, xp2 = zip(*sorted(xp))

        xp1_dic[profile_key] = xp1
        xp2_dic[profile_key] = xp2

    return xp1_dic, xp2_dic


def load_profiles_data(aligfile: str):
    full_dic = load_dic_file(aligfile)

    cores_dic = {key: value for key, value in full_dic["cores"].items() if key != "REF"}
    ref_dic = full_dic["cores"]["REF"]

    return ref_dic, cores_dic
