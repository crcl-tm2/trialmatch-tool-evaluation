# A Prospective Pragmatic Evaluation of Automatic Trial Match Tools in a Molecular Tumor Board

Numerous publicly available automatic trial matching tools help patients and their caregivers searching all the possible clinical trials related to certain health conditions. While this technology can enhance access to therapeutic innovations, frequent errors may expose to over-solicitation and disappointment. This study evaluates the performance of these tools.

# Development setup

This following packages should be installed
* python
* poetry
* git

Clone the repository:
```shell
git clone https://github.com/crcl-tm2/trialmatch-tool-evaluation
cd trialmatch-tool-evaluation
```

Install dependencies using Poetry:
```shell
poetry install
```

Alternatively, you can use `pip` to install dependencies from the `requirements.txt` file:
```shell
pip install -r requirements.txt
```

# Running the evaluation

Run the evaluation using the `main.py` script:

```shell
python trialmatch-tool-evaluation/main.py
```