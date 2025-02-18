import re
from utils import clean_text_paragraph

def generate_prompt_summarization(commit):
    """
    Generate a prompt for summarizing a git commit.
    """
    prompt = f"""
        You are a helpful assistant. Provide a concise description of what has been done in the following commit:

        Commit Infomations:
        - Hash (unique identifier): {commit['hash']}
        - Author: {commit['author']}
        - Date: {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}

        Commit Message - this provides a brief summary of the changes:
        {commit['message']}

        Changed Files - files modified in this commit:
        {', '.join(commit['files'])}

        Diffs - lines of code changed in each file, use this to understand the specific changes:
        {chr(10).join([f"{file_name}: {diff[:1000]}" for file_name, diff in commit['diffs'].items()])}

        Use all the informations available to analyze the changes focusing on the purpose, key changes, and significance.
        Exclude unnecessary technical details and make it easy to understand for a project manager or developer.

        Do not repeat the prompt. Do no repeat any of the information provided above. Do not include lines of code

        Answer:
        """
    prompt = clean_text_paragraph(prompt)
    return prompt


def generate_prompt_summarization_few_shots(commit):
    prompt = f"""
        You are a helpful assistant. Provide a concise description of what has been done in the following commits.

        Example 1:
        Commit Informations:
        - Hash (unique identifier): 1a2b3c4d
        - Author: John Doe
        - Date: 2025-01-01 10:00:00
        Commit Message - this provides a brief summary of the changes:
        Refactored the user authentication module to improve performance and readability.
        Changed Files - files modified in this commit:
        auth.py, user_model.py
        Diffs - lines of code changed in each file:
        auth.py:
        ```diff
        - def authenticate_user(username, password):
        -     if username and password:
        -         return check_credentials(username, password)
        + def authenticate_user(user_credentials):
        +     return validate_user(user_credentials)
        ```
        user_model.py:
        ```diff
        + def validate_user(credentials):
        +     # New validation logic for login
        +     return is_valid(credentials)
        ```
        Answer:
        Refactored the user authentication system to improve both performance and readability.
        Key changes include replacing the `authenticate_user` function to accept a `user_credentials` object instead of separate username and password arguments, simplifying the interface and making the code less error-prone.
        Additionally, a new `validate_user` function was introduced in `user_model.py` to centralize login validation logic, improving modularity and enabling easier future updates.
        These changes make the authentication process more robust and align with modern software design principles.

        Example 2:
        Commit Informations:
        - Hash (unique identifier): 5e6f7g8h
        - Author: Jane Smith
        - Date: 2025-01-02 14:30:00
        Commit Message - this provides a brief summary of the changes:
        Added a new feature for exporting reports to CSV.
        Changed Files - files modified in this commit:
        report_exporter.py, utils/csv_writer.py
        Diffs - lines of code changed in each file:
        report_exporter.py:
        ```diff
        + def export_to_csv(data, filename):
        +     with open(filename, 'w') as file:
        +         writer = csv.writer(file)
        +         writer.writerow(data.keys())
        +         writer.writerows(data.values())
        ```
        utils/csv_writer.py:
        ```diff
        + import csv
        ```
        Answer:
        Added a new feature for exporting reports to CSV format, enabling users to easily extract structured data.
        Key changes include introducing the `export_to_csv` function in `report_exporter.py`, which uses Python’s built-in CSV library to create files with appropriate headers and rows based on the input data.
        The `utils/csv_writer.py` module was also updated to include CSV-related utilities, promoting code reuse and reducing duplication across the project.
        This enhancement significantly improves the usability of the reporting system, particularly for end users who need seamless integration with external tools like Excel.

        Example 3:
        Commit Informations:
        - Hash (unique identifier): b2c4d6e8
        - Author: Alice Brown
        - Date: 2024-03-15 16:42:10
        Commit Message - this provides a brief summary of the changes:
        Fixed scope handling for function declarations in JavaScript compilation.
        Changed Files - files modified in this commit:
        jscompiler.c
        Diffs - lines of code changed in each file:
        jscompiler.c:
        ```diff
        - static void compile_function_body(JF, js_Ast *name, js_Ast *params, js_Ast *body, int is_fun_exp);
        + static void compile_function_body(JF, js_Ast *name, js_Ast *params, js_Ast *body);
        - static js_Function *create_function(js_State *J, int line, js_Ast *name, js_Ast *params, js_Ast *body, int script, int strict, int is_fun_exp);
        + static js_Function *create_function(js_State *J, int line, js_Ast *name, js_Ast *params, js_Ast *body, int script, int strict);
        ```
        Answer:
        Addressed an issue with scope handling for function declarations in the JavaScript compiler.
        The key change involved removing the `is_fun_exp` parameter from the `compile_function_body` and `create_function` methods, simplifying the handling of function declaration bindings.
        This improves code clarity and correctness, ensuring that function declarations adhere to the expected scope rules.
        These updates pave the way for further improvements, such as making function expression bindings immutable, which aligns with the long-term goals for the compiler's behavior.


        Now analyze the following commit:

        Commit Informations:
        - Hash (unique identifier): {commit['hash']}
        - Author: {commit['author']}
        - Date: {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}
        Commit Message - this provides a brief summary of the changes:
        {commit['message']}
        Changed Files - files modified in this commit:
        {', '.join(commit['files'])}
        Diffs - lines of code changed in each file:
        {chr(10).join([f"{file_name}: {diff[:1000]}" for file_name, diff in commit['diffs'].items()])}

        Use all the informations available to analyze the changes focusing on the purpose, key changes, and significance.
        Exclude unnecessary technical details and make it easy to understand for a project manager or developer.

        Do not repeat the prompt. Do no repeat any of the information provided above. Do not include lines of code
        Answer:
    """
    prompt = clean_text_paragraph(prompt)
    return prompt



def ask_model_summarization(prompt, pipe):
    """
    Ask the model to summarize a git commit.
    """
    answer = pipe(
        prompt,
        max_new_tokens=200,
        do_sample=False,
        temperature=None,
        top_p=None,
    )[0]['generated_text']

    answer = answer.split("Answer:")[-1]
    return answer

