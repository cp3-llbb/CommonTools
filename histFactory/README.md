## Build instructions

```bash
cd external
./build-external.sh
cd ..

make
```

## How to use

```bash
# get the correct environment
source ../setup_env.sh
# Create the histos
./createHistoWithMultiDraw.exe -d samples/mysamples.json plots/myplots.json
```
