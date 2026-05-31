import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / "data" / "batadal2.zip"
OUT_TRAIN = ROOT / "data" / "batadal_train.csv"
OUT_TEST = ROOT / "data" / "batadal_test.csv"
SEED = 42
TEST_FRACTION = 0.3


def canon(col):
    if col == "timestamp":
        return "DATETIME"
    if col == "iteration":
        return None
    if re.fullmatch(r"T\d+", col):
        return "L_" + col
    if re.fullmatch(r"(PU\d+|V\d+)F", col):
        return "F_" + col[:-1]
    if re.fullmatch(r"(PU\d+|V\d+)", col):
        return "S_" + col
    if re.fullmatch(r"J\d+", col):
        return "P_" + col
    return col


def attack_columns(z, gt_path):
    with z.open(gt_path) as f:
        head = pd.read_csv(f, nrows=0)
    return [c for c in head.columns if "attack" in c.lower()]


def load_batch(z, scada_path, gt_path, is_attack):
    with z.open(scada_path) as f:
        s = pd.read_csv(f).sort_values("iteration").reset_index(drop=True)
    att = np.zeros(len(s), dtype=int)
    if is_attack:
        cols = attack_columns(z, gt_path)
        if cols:
            with z.open(gt_path) as f:
                g = pd.read_csv(f, usecols=["iteration"] + cols)
            g = g.sort_values("iteration").reset_index(drop=True)
            flag = (g[cols].fillna(0).to_numpy() > 0).any(axis=1).astype(int)
            n = min(len(flag), len(att))
            att[:n] = flag[:n]
    out = {}
    for c in s.columns:
        nc = canon(c)
        if nc is not None:
            out[nc] = s[c].to_numpy()
    df = pd.DataFrame(out)
    df["ATT_FLAG"] = att
    cont = [c for c in df.columns if c not in ("DATETIME", "ATT_FLAG") and not c.startswith("S_")]
    ref = df.loc[df["ATT_FLAG"] == 0, cont]
    if len(ref) < 30:
        ref = df[cont]
    mu = ref.mean()
    sd = ref.std().replace(0, 1.0)
    df[cont] = (df[cont] - mu) / sd
    return df


def batch_pairs(z):
    names = set(z.namelist())
    pairs = []
    for sp in sorted(n for n in names if n.endswith("/scada_values.csv")):
        gp = sp.replace("scada_values.csv", "ground_truth.csv")
        if gp in names:
            pairs.append((sp, gp, sp.startswith("evasion_data/")))
    return pairs


def split(group, rng):
    idx = rng.permutation(len(group))
    n_test = int(round(len(group) * TEST_FRACTION))
    test_ids = set(idx[:n_test].tolist())
    train = [group[i] for i in range(len(group)) if i not in test_ids]
    test = [group[i] for i in range(len(group)) if i in test_ids]
    return train, test


def build(z, pairs, label):
    frames = []
    for k, (sp, gp, ia) in enumerate(pairs):
        frames.append(load_batch(z, sp, gp, ia))
        if (k + 1) % 10 == 0 or k + 1 == len(pairs):
            print(label, "processed", k + 1, "of", len(pairs))
    return pd.concat(frames, ignore_index=True)


def main():
    z = zipfile.ZipFile(ZIP)
    pairs = batch_pairs(z)
    normal = [p for p in pairs if not p[2]]
    attack = [p for p in pairs if p[2]]
    print("batches found: normal", len(normal), "attack", len(attack))
    rng = np.random.default_rng(SEED)
    ntr, nte = split(normal, rng)
    atr, ate = split(attack, rng)
    train_df = build(z, ntr + atr, "train")
    test_df = build(z, nte + ate, "test")
    train_df.to_csv(OUT_TRAIN, index=False)
    test_df.to_csv(OUT_TEST, index=False)
    print("train", train_df.shape, "attack_rows", int(train_df["ATT_FLAG"].sum()))
    print("test", test_df.shape, "attack_rows", int(test_df["ATT_FLAG"].sum()))
    print("feature columns", [c for c in train_df.columns if c not in ("DATETIME", "ATT_FLAG")][:10], "...")


if __name__ == "__main__":
    main()
