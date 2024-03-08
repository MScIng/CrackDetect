# crackdetect

To pull files using dvc:
```
dvc pull
```


Created using [mlops_template](https://github.com/SkafteNicki/mlops_template),
a [cookiecutter template](https://github.com/cookiecutter/cookiecutter) for getting
started with Machine Learning Operations (MLOps).

# Virtual environment in powershell
Have `python >= 3.10`?
1. `python -m venv fleetenv` -- Create environment
2. Add `$env:PYTHONPATH += ";Absolute\path\to\CrackDetect\src"` to `fleetenv\Scripts\Activate.ps1` at the end before signature block.
3. `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` -- Change execution policy if necessary (to be executed in powershell)
4. `.\fleetenv\Scripts\Activate.ps1` -- Activate venv
5. `python -m pip install -U pip setuptools wheel`
6. `python -m pip install -r requirements.txt`
7. ...
8. Profit