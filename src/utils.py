import re, os, pickle
from git import Repo
from matplotlib import pyplot as plt
from collections import defaultdict

def filter_diff_lines(diff_text):
    """
    Filters the lines of a Git diff, keeping only those that start with '+' or '-',
    excluding file headers ('+++', '---').

    Args:
        diff_text (str): The text of the Git diff.

    Returns:
        str: The filtered lines of the diff.
    """
    filtered_lines = []
    for line in diff_text.splitlines():
        # Include lines that start with '+' or '-' but exclude '+++' or '---'
        if (line.startswith('+') or line.startswith('-')) and not line.startswith('+++') and not line.startswith('---'):
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def extract_git_commits(repo_path, branch='master'):
    """
    Extracts commit information from a Git repository.
    """
    repo = Repo(repo_path)
    commits = list(repo.iter_commits(branch))
    commits_dict = {}

    for i, commit in enumerate(commits):
        commits_dict[i] = {
            'hash': commit.hexsha,
            'author': f"{commit.author.name} <{commit.author.email}>",
            'date': commit.authored_datetime,
            'message': commit.message.strip(),
            'files': list(commit.stats.files.keys()),
            'diffs': {},
            'llama_summary': '',
            'llama_category': '',
            'llama_tech_summary': ''
        }

        diffs = commit.diff(commit.parents[0] if commit.parents else None, create_patch=True)

        for diff in diffs:
            file_diff = diff.diff.decode('utf-8')
            file_name = f"{diff.a_path} -> {diff.b_path}" if diff.a_path != diff.b_path else diff.a_path
            commits_dict[i]['diffs'][file_name] = filter_diff_lines(file_diff)

    print(f"Extracted {len(commits_dict)} commits")
    return commits_dict


def filter_trivial_commits(commits_dict, trivial_patterns=None, min_diff_lines=5):
    """
    Filters out trivial commits based on patterns and diff size.
    To add a new trivial pattern, add it to the trivial_patterns list below.
    """

    if trivial_patterns is None:
        trivial_patterns = [
            r"merge branch",        # Merging branches
            r"fix typo",            # Fixing typos
            r"readme",              # Updating documentation
            r"minor",               # General minor changes
            r"release",             # Release versions
            r"cleanup"              # Cleanups
        ]

    filtered_commits = {}
    filtered_number = 0

    for index, commit in commits_dict.items():
        # Check commit message for trivial patterns
        if any(re.search(pattern, commit['message'], re.IGNORECASE) for pattern in trivial_patterns):
            filtered_number += 1
            continue

        # Check diff size (number of lines changed)
        total_diff_lines = sum(len(diff.splitlines()) for diff in commit['diffs'].values())
        if total_diff_lines < min_diff_lines:
            filtered_number += 1
            continue

        # If commit passes all filters, include it
        filtered_commits[index] = commit

    print(f"Filtered {filtered_number} commits")
    return filtered_commits


def normalize_commit_data(commit_data):
    """
    Normalize all commit messages in a dictionary of git data.
    """

    def normalize_message(message):
        """
        Normalize a single git commit message.
        """
        # Remove leading/trailing whitespace and ensure capitalization
        normalized = message.strip().capitalize()

        # Replace multiple spaces or tabs with a single space
        normalized = re.sub(
          r'\s+', ' ', normalized)

        # Remove repetitive or excessive comments like "!!!!!" or "..."
        normalized = re.sub(r'[!?.]{2,}', '.', normalized)

        # Eliminate redundant phrases or filler words
        redundant_phrases = [
            r"\bthis commit\b", r"\bminor fix\b", r"\bsmall update\b",
            r"\bquick fix\b", r"\btemporary change\b", r"\btest commit\b"
        ]
        for phrase in redundant_phrases:
            normalized = re.sub(phrase, '', normalized, flags=re.IGNORECASE).strip()

        # Simplify common patterns
        normalized = re.sub(r'\bAdded\b', 'Add', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\bRemoved\b', 'Remove', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\bFixed\b', 'Fix', normalized, flags=re.IGNORECASE)

        # Standardize specific keywords
        normalized = re.sub(r'\bBugfix\b', 'Bug fix', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\bRefactored\b', 'Refactor', normalized, flags=re.IGNORECASE)

        # Ensure the message ends with a period if it doesn't already
        if not normalized.endswith('.'):
            normalized += '.'

        return normalized

    # Iterate through each commit and normalize the message
    for index, commit in commit_data.items():
        if "message" in commit:
            commit["message"] = normalize_message(commit["message"])

    print("Normalize commits done")
    return commit_data

def clean_text_paragraph(text):
    """
    Cleans a text paragraph by removing unnecessary blank lines
    and excessive indentation.
    """
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = "\n".join(cleaned_lines)

    return cleaned_text


def plot_categories(commits, shot_method):
    commit_counts = defaultdict(lambda: defaultdict(int))

    def get_quarter(date):
        month = date.month
        quarter = (month - 1) // 3 + 1  # Calculate the quarter (1 to 4)
        return f"{date.year}-Q{quarter}"

    for idx, commit in commits.items():
        if commit['llama_category'] == '':
            continue
        quarter = get_quarter(commit['date'])
        category = commit['llama_category']
        commit_counts[category][quarter] += 1

    categories = commit_counts.keys()
    quarters = sorted({quarter for category_data in commit_counts.values() for quarter in category_data})  # Sorted unique quarters

    plt.figure(figsize=(10, 6))
    for category in categories:
        counts = [commit_counts[category][quarter] if quarter in commit_counts[category] else 0 for quarter in quarters]
        plt.plot(quarters, counts, marker='o', label=category)

    plt.title('Commit Classification Over Time')
    plt.xlabel('Quarter')
    plt.ylabel('Number of Commits')
    plt.legend(title='Category for Llama')
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.tight_layout()

    # Show the plot
    plt.show()

    plt.savefig(f"plot_categories_{shot_method}.svg", format="svg")


def plot_categories_piechart(commits,shot_method):
    commit_counts = defaultdict(int)

    for idx, commit in commits.items():
        if commit['llama_category'] == '':
            continue
        category = commit['llama_category']
        commit_counts[category] += 1

    categories = commit_counts.keys()
    counts = [commit_counts[category] for category in categories]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Commit Classification Pie Chart')
    plt.show()
    plt.savefig(f"plot_categories_piechart_{shot_method}.svg", format="svg")

def full_path(DATA_FILEPATH, name_file):
  path = os.path.join(DATA_FILEPATH, f"commits_{name_file}.pkl" )
  return path

def save_commits(commits, file_path):
    """
    Save commits to a file using pickle, creating directories if they do not exist.
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Now save the commits to the file
    with open(file_path, "wb") as file:
        pickle.dump(commits, file)
    #print(f"Commits saved to {file_path}")

def load_commits(file_path):
    """
    Load commits from a file if available.
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            return pickle.load(file)
    return None


def save_variable(variable, file_path):
    """
    Save a variable to a file using pickle, creating directories if they do not exist.

    :param variable: The variable to save.
    :param file_path: The path of the file to save the variable to.
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Now save the variable to the file
    with open(file_path, "wb") as file:
        pickle.dump(variable, file)
    print(f"Variable saved to {file_path}")
    
    
def calculate_precision_recall_categorization(commits, ground_truth):
  """
  Returns the precision and recall of the commits.
  Note that ground_truth is a list where ground_truth[i] is the category of the i-th commit.
  Should be handcrafted or GPT generated.
  """

  TP = 0
  TN = 0
  FP = 0
  FN = 0

  for i, commit in commits.items():
    if i >= 100:
      break
    predicted = commit['llama_category']
    actual = ground_truth[i]
    if predicted == actual:
      if predicted == 'Other':
        TN += 1
      else:
        TP += 1
    else:
      if predicted == 'Other':
        FN += 1
      else:
        FP += 1

  accuracy = (TP + TN) / (TP + TN + FP + FN)
  precision = TP / (TP + FP) if TP + FP > 0 else 0
  recall = TP / (TP + FN) if TP + FN > 0 else 0

  return precision, recall, accuracy