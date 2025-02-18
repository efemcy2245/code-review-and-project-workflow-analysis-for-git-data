import os
import torch
import copy
from tqdm import tqdm
from transformers import pipeline
from utils import load_commits, save_commits, full_path
from utils import extract_git_commits, filter_trivial_commits, normalize_commit_data
from utils import plot_categories, plot_categories_piechart
from categorization import ask_model_categorization, generate_prompt_categorization_few_shots, generate_prompt_categorization_zero_shot
from summary import ask_model_summarization, generate_prompt_summarization_few_shots, generate_prompt_summarization
from tech_summary import generate_technical_report

#from huggingface_hub import login
#login() # Add Hugging Face token

DEVICE_USED = 0 if torch.cuda.is_available() else -1
REMOTE_PATH = 'https://github.com/ccxvii/mujs.git'
LOCAL_PATH = './mujs'
CURRENT_DIRECTORY = os.getcwd()
PIPE_LLAMA = pipeline("text-generation", model="meta-llama/Llama-3.2-1B-Instruct", pad_token_id=128001, device=DEVICE_USED)

# Avoid warning related to parallelization
os.environ["TOKENIZERS_PARALLELISM"] = "false"

if not os.path.isdir(LOCAL_PATH):
    os.system(f"git clone {REMOTE_PATH} {LOCAL_PATH}")

DATA_FILEPATH_RAW_DATA = 'commits_raw.pkl'
DATA_FILEPATH_ZERO_SHOT = 'commits_zero_shot.pkl'
DATA_FILEPATH_FEW_SHOTS = 'commits_few_shots.pkl'

commits = load_commits(DATA_FILEPATH_RAW_DATA)  # To resume experiments
commits_zero_shot = load_commits(DATA_FILEPATH_ZERO_SHOT)  # To resume experiments
commits_few_shots = load_commits(DATA_FILEPATH_FEW_SHOTS)  # To resume experiments

if commits is None:  # If there are no checkpoints, initialize commits extraction
    commits = extract_git_commits(LOCAL_PATH)  # Extract commits from repository
    commits = filter_trivial_commits(commits)  # Filter trivial commits
    commits = normalize_commit_data(commits)  # Normalize commits
    commits = {i: value for i, value in enumerate(commits.values())}  # Adjust idxs
    save_commits(commits, full_path(CURRENT_DIRECTORY, "raw"))
    
# Run Few-Shot and Zero-Shot experiments

if commits_few_shots is None:
  commits_few_shots = copy.deepcopy(commits)

for i, (idx, commit) in tqdm(enumerate(commits_few_shots.items())):
    # Run summarization and categorization only on unprocessed commits
    if not commit['llama_summary'] and i < 100:
      prompt = generate_prompt_summarization_few_shots(commit)
      commit['llama_summary'] = ask_model_summarization(prompt, PIPE_LLAMA)
    if not commit['llama_category']:
      prompt = generate_prompt_categorization_few_shots(commit)
      commit['llama_category'] = ask_model_categorization(prompt, PIPE_LLAMA)
    save_commits(commits_few_shots, full_path(CURRENT_DIRECTORY,"few_shots"))

plot_categories(commits_few_shots, "few_shots")
plot_categories_piechart(commits_few_shots,"few_shots")



if commits_zero_shot is None:
  commits_zero_shot = copy.deepcopy(commits)

for i, (idx, commit) in tqdm(enumerate(commits_zero_shot.items())):
    # Run categorization only on unprocessed commits
    if commit['llama_category']:
      prompt = generate_prompt_categorization_zero_shot(commit)
      commit['llama_category'] = ask_model_categorization(prompt, PIPE_LLAMA)
    save_commits(commits_zero_shot, full_path(CURRENT_DIRECTORY,"zero_shot"))

plot_categories(commits_zero_shot, "zero_shot")
plot_categories_piechart(commits_zero_shot, "zero_shot")

# Generate technical summaries for few-shot commits

for idx, (i, commit) in tqdm(enumerate(commits_few_shots.items())):
  if 'llama_tech_summary' not in commit:
    commit['llama_tech_summary'] = generate_technical_report(commit)
    #print(f"Processed commmit {idx+1}/{len(commits_few_shots)}")
  save_commits(commits_few_shots, full_path(CURRENT_DIRECTORY,"few_shots"))
