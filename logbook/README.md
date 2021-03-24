1. Requires redis to be installed

2. Set up environment with conda:
```
conda env create --file=environment.yml
conda activate ssw215
```

3. Put your github access token in a file called `token`
4. Run it
```
./logbook/autologbook.py
```