# Traffic accidents in Wroclaw city

Spatial data processing project lab

__Authors__: Michał Kajstura, Maciej Ziółkowski, Joanna Baran

## Dataset

TODO: write description

### DVC

All data are managed by [DVC](https://dvc.org/) tool. Data files are directly added to
remote repository. Just run `dvc pull` to download them.

### Installation

```
conda create --yes -c conda-forge -n <name> python=3.8 osmnx  
pip install -r requirements.txt
```