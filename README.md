# PFC-Tritium-Transport

This repository contains `hisp` (see https://github.com/festim-dev/hisp) scripts and plasma data that are tailored for ITER.

## How to Install:

Clone the repository and checkout to the relevant branch
```
git clone https://github.com/iterorganization/PFC-Tritium-Transport
cd PFC-Tritium-Transport
git checkout ...
```
Prepare the Python virtual environment (myenv).
```
ml IMAS
ml Python
python -m venv myenv
source myenv/bin/activate

pip install plotly
ml foss
ml SciPy-bundle 
ml mpi4py
ml tqdm
ml scifem
ml dolfinx/0.9.0-foss-2023b

# install custom festim
python -m pip install git+https://github.com/festim-dev/FESTIM@d1b71deed2d0998159b99591951493bffa1f5ca8

# install custom hisp
python -m pip install git+https://github.com/festim-dev/hisp@fix-b-bins
```
## How to Run:

Prepare your batch job 'job.sh' in folder 'run_on_cluster'. Open a terminal in folder PFC-Tritium-Transport. Submit job using 
```
sh run_on_cluster/job.sh
```

