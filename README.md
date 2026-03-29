# RAW: Rules As Written - D&D 5e LLM Evaluation

**Rules As Written** is an investigation into the potential useof Large Language Models (LLMs) and Retrievail-Augmented Generation (RAG) frameworks as rule-assistance tools for tabletop role playing games (TTRPGs), specifically Dungeons and Dragons 5th Edition.

It attempts to evaluate 3 different proprietary LLMs:

- **OpenAI** - GPT-5.4
- **Anthropic** - Claude Opus 4.6
- **Google** - Gemini 3.1 Pro Preview _(which had to be disabled due to rate limit issues)_

This project focuses on 2 main strategies for comparison, **Context-Stuffing** and **RAG Frameworks**.

While this particular repo is specific to Dungeons and Dragons 5th Edition rules, the data and models can easily be changed if someone wishes to utilize it for their own LLM assessment.

## Utilized Technology

### Language

- Python 3.11.1 (in venv)

### LLM APIs

| Package | Model Version |
| --- | --- |
| `anthropic` | Claude Opus 4.6 API |
| `openai` | GPT-5.4 API |
| `google.genai` | Gemini 3.1 Pro Preview |

### RAG Packages

| Package | Use |
| --- | --- |
| `sentence-transformers` | `all-MiniLM-L6-v2` embedding model (converts text to numerical vectos) |
| `faiss` | Facebook AI Similarity Search (vector index) |
| `langchain-text-splitters` | Chunking document - header and recursive character |

### PDF Conversion

| Package | Use |
| --- | --- |
| `pymupdf` , `fitz` | Initial conversion attempt, extremely simple |
| `pymupdf4llm` | PDF-to-Markdown conversion, utilised in project |
| `marker-pdf` | GPU PDF Conversion (crashed in my implementation, so not used) |

### Data and Analysis

| Package | Use |
| --- | --- |
| `pandas` | CSV handling and DataFrame (table) aggregation |
| `numpy` | Numerical and scientific computing - used for arrays |
| `bert-score` | BERTScore semantic similarity metric for LLM responses |
| `matplotlib` | Creating charts and data visualizations |
| `openpyxl` | Writes excel files, used in json coversions |
| `python-dotenv` | Loading information for `.env` file |

## Set-up Environment

### Prerequisites

- Python 3.11.1 (at least) - if using different version ensure compatibility with other packages
- pip - needed to install packages
- Python Virtual Environment (venv)

### Virtual Environment

_NB: Commands will be relevant for Ubuntu Linux, adjust for your os._

```bash
# Update package lists
sudo apt update
sudo apt full-upgrade-y

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate 
```

### Install Dependencies

Required packages:
```bash
pip install anthropic openai google-genai # or whatever models you wish to use
pip install sentence-transformers faiss-cpu
pip install langchain langchain-text-splitters
pip install pymupdf pymupdf4llm
pip install pandas numpy openpyxl matplotlib
pip install bert-score python-dotenv
```

_Note: If you wish to use `marker-pdf` to convert a pdf, that will also need to be installed. You can replace `pymupdf` `pymupdf4llm` if not using them._

## Configuration

### API Keys

API Keys are sensitive and secure, so should be stored in a `.env` file which is listed in `.gitignore`. Do not commit them to your version control

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_antrhopic_api_key
GOOGLE_API_KEY=your_google_api_key
```

These can be adjusted based on whatever model APIs you wish to use in your evaluation.

### Model Information and Settings

When generating answers from the model, there are 2 parameters that can be set to adjust/influence how the model responds:

- `max_tokens` sets a maximum number of output tokens for a response - can be used to limit cost, but can affect results
- `temperature` determines how the model answers - low temperatures ensure that it is deterministic and factual, higher temperatures allow for more creativity

Another parameter to call out is used when creating the `rag_pipline` which is `Top-K`. This paramets allows you to set the number of chunks fed to the model as context.

Also, prices are currently **hardcoded** in `model_wrap.py` and should be updated if using a different model or if prices change. _(Accurate as of March 2026)_

## Implementation

### Adjust Scripts

If you wish to use this repo as is, you can skip ahead and just run the relevant bash commands to run the python scripts.

However, if you wish to use this as a template for your own data and evaluation, you will first need to review and adjust the scripts to include the correct names and paths for your data and outcomes.

### Simple Steps

1. Convert Source PDF to Markdown - this can take some time and may require a human review to ensure correct formatting
2. Covert Evaluation Questions from CSV to JSONL - this only needs to be run once, if data is already in jsonl format, does not need to run again
3. Build FAISS Index - already built in this repo, only run again if source document changes
4. Run Context-Stuffing Evaluation - this runs through your eval data set and generates responses, can take time depending on the models used
5. Run RAG Evaluation - runs through rag eval script by retrieving the top 5 most relevant chunks for the question asked, only responds based on those chunks
6. Scoring Results - this could be done manually depending on the size of your dataset and results. Included scripts utilise BERTScoring and LLM-as-Judge methods to automatically assess results
7. Data Analysis & Visualisation - generate tables and charts that can be easily read by a person to better understand results

#### General Format when running scripts

```bash
python your-script-name
```

_Note: if your script is in another directory to where you are currently (ie you are in `main` but the script is in a subdirectory), please ensure that you are using the correct path to call the script._

## Dataset

For the initial run of this project, I only assessed 33 questions found in `eval-questions/eval_questions_1.jsonl` as I was limited by time and cost restrictions. However, there are 3 additional files in csv format that could be used to increase the dataset for more accurate and detailed results. This repo also includes one large dataset file `eval-questions/all_eval_questions.csv` which includes all 137 questions from the other files in one as a single larger dataset.

### Taxonomy

The `taxonomy` directory was added in the hopes of being able to implement InstructLab to create synthetic data and further bolster my results. However, when trying to run instrcutlab using my gpu, it kept crashing before generating any usable data. If you wish to use InstructLab, `taxonomy` can be used as an example of how your seed data should be formatted for your teacher model.

#### InstructLab Steps

While this may not have worked out for me, I will provide the basic steps to get you started if this is something you would like to use.

##### Install & Configure

```bash
# Install InstructLab
pip install instructlab

# Verify installation
ilab --version

# Initialise ilab
ilab config init

# Download Teacher model - defaults to merlinite-7b-lab-GGUF
ilab model download
```

This method does run InstructLab locally, if that is not something your laptop can handle (especially if creating large synthetic data sets) you should look into implementing a model API instead.

##### Create Taxonomy

Here you will create your topic folder _inside_ instructlab's taxonomy folder. This is already created when your download and initialize instructlab, you do not need to create a new taxonomy folder, just the topic folder.

Within your topic folder, you will create a qna.yaml file, as seen in the existing `taxonomy` directory. This is what is used to indicate to the teacher the kind of data that you are looking for it to create. Each topic needs a minimum of 5 `seed_examples` to be effective.

You must also include an `attribution.txt` file within your topic folder. This contains the necessary information about your source document such as title, license, and source.

Once your taxonomy is created, run:

```bash
ilab taxonomy diff
```

This will catch any errors in your taxonomy before you try to generate data with it.

##### Generate Data

```bash
# Generate full pipeline - high quality, more in-depth
ilab data generate --pipeline full --sdg-scale-factor 10

# Generate simple pipeline - lower quality, much faster
ilab data generate --pipeline full --sdg-scale-factor 10
```

The pipeline for instructlab is essentially just how the data is created. `simple` is the default, and is a lightweight and faster method of generation but can be lower quality. `full` runs the complete generation pipeline and creates more diverse and high-quality examples, however, it can be much slower.

`--sdg-scale-factor` sets the number of examples created for each seed example. So if you have 5 seed examples in your topic `qna.yaml`, and you set `--sdg-scale-factor` to 10, it should generate 50 new, synthetic examples.

If this runs correctly, you should have your synthetic data created in a jsonl format, which can be used easily in the above evaluation steps. It is always recommended that you should manually evaluate the synthetic data before using just to ensure that it is correct for your purpose.

If your synthetic data jsonl saves to you instructlab directory, just ensure to copy it to your evaluation directory in order to correctly utilise it.

## Known Issues & Limitations

- Gemini Disabled: When trying to utilise my gemini api it maxed out its Tokens per Minute (TPM) limit after only a few questions. I believe this is caused because all of the questions are loaded into the model at once to assess, but I would need to further investigate in order to solve.
- Marker PDF Crash: From my research, this is supposed to be an excellent converter, especially when structure is so necessary to a documents. However, it has a gpu requirement which appeared to kill the process on every run. Leveraged `pymupdf4llm` for document conversion instead, but did require a lot of manual editing.
- Small Evaluation Set: Results would potentially be more accurate with a larger dataset. Additional datasets available to use in repor, but was unable to test due to time and cost limitations.
