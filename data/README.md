# Datasets

The notebook expects two CSV files in this folder:

```
data/batadal_train.csv
data/batadal_test.csv
```

If these are absent, the notebook falls back to a synthetic BATADAL-like sample (clearly
flagged) so the pipeline can be validated end-to-end before real data is downloaded.

## BATADAL 2.0 (recommended, 2024)

Generated with the DHALSIM co-simulator (SUTD / TU Delft / CISPA / iTrust). Unlike the 2016
BATADAL, it combines **process data with network traces** of PLCs and the SCADA server, which
enables the `affected_layer = process | network | cyber-physical` distinction.

Steps:

1. Download `dataset.zip` (about 20.9 GB) from Zenodo and place it at `data/batadal2.zip`:
   https://zenodo.org/records/13692004
2. Build the train/test CSVs (reads directly from the zip, no full extraction needed):

   ```
   python scripts/prepare_batadal2.py
   ```

   This produces `data/batadal_train.csv` and `data/batadal_test.csv` by renaming the SCADA
   columns to the canonical scheme (`L_T*`, `F_PU*`, `S_PU*`, `P_J*`), deriving `ATT_FLAG`
   from the `ground_truth.csv` attack columns, and splitting batches 70/30 across the normal
   and attack scenarios.

The dataset layout inside the zip is `normal_operating_conditions_*/output/batch_N/` and
`evasion_data/attack_output_*/`, each batch holding `scada_values.csv` (operator-visible SCADA
readings), `ground_truth.csv` (true state plus `*attack*` label columns), and per-PLC
`*.pcap.gz` network captures. The network captures are not yet parsed; the process layer is
used first and the network layer (Modbus/TCP indicators) is a planned extension.

- DHALSIM simulator: https://github.com/Critical-Infrastructure-Systems-Lab/DHALSIM
- Dataset publication: Murillo et al., "A Thorough Cybersecurity Dataset for Intrusion
  Detection in Smart Water Networks", WDSA/CCWI 2022.

## BATADAL 1.0 (fallback, 2016)

Process data only (tank levels, flows, pump/valve states, junction pressures) with an
`ATT_FLAG` attack label. Smaller and immediately downloadable from https://www.batadal.net/.

## Loading conventions

The loader strips whitespace from column names and auto-detects:

- the timestamp column (`DATETIME`, `TIMESTAMP`, `TIME`, `DATE`);
- the label column (`ATT_FLAG`, `ATTACK`, `LABEL`, ...), where any value `> 0` is an attack;
- numeric feature columns, grouped by prefix into levels (`L_`), flows (`F_`),
  statuses (`S_`), pressures (`P_`).

Rename your downloaded files to `batadal_train.csv` / `batadal_test.csv`, or edit
`TRAIN_FILE` / `TEST_FILE` in the configuration cell.
