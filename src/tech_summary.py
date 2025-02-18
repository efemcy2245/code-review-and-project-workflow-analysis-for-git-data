from utils import clean_text_paragraph

def generate_prompt_technical_analysis(commit, comment=None):
  """
  Generate the prompt for the technical analysis, if a comment from QA is present it is incorporated in the prompt.
  """

  prompt = f"""
        You are an expert developer and code reviewer. Analyze the following code diffs from a commit and provide a detailed technical explanation of the changes, including any potential impact on functionality, performance, or correctness.

        Use the following format:
        - **Summary of Changes**: A brief summary of the changes made in the diff.
        - **Functionality**: Describe how these changes affect the functionality of the code.
        - **Performance**: Mention any impact on performance, if applicable (e.g., optimizations, changes in computational complexity).
        - **Correctness**: Discuss any potential correctness issues or improvements.
        - **Other Considerations**: Any other relevant points, such as code style, readability, or maintainability.

        Example 1:
        Commit Informations:
        - Hash (unique identifier): a1b2c3d4
        - Author: John Doe
        - Date: 2025-01-01 10:00:00
        Commit Message - this provides a brief summary of the changes:
        Refactored the user authentication module to improve performance and readability.
        Changed Files - files modified in this commit:
        auth.py
        Diffs - lines of code changed in each file:
        auth.py:
        ```diff
        - def authenticate_user(username, password):
        -     if username and password:
        -         return check_credentials(username, password)
        + def authenticate_user(user_credentials):
        +     return validate_user(user_credentials)
        ```
        Summary of Changes: The `authenticate_user` function was refactored to accept a `user_credentials` object instead of separate `username` and `password` arguments.
        Functionality: This change simplifies the function interface, reducing the number of arguments and making it easier to maintain and extend.
        Performance: The performance impact is negligible, as the logic is functionally equivalent, but the refactor improves code readability.
        Correctness: No impact on correctness, assuming that `validate_user` is correctly implemented and that `user_credentials` contains all necessary data.
        Other Considerations: This change improves code maintainability by introducing a more modular approach to handling user authentication.

        Example 2:
        Commit Informations:
        - Hash (unique identifier): e5f6g7h8
        - Author: Alice Brown
        - Date: 2025-02-02 12:30:00
        Commit Message - this provides a brief summary of the changes:
        Fixed scope handling for function declarations in the JavaScript compiler.
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
        Summary of Changes: The `is_fun_exp` parameter was removed from both the `compile_function_body` and `create_function` functions to simplify function declaration handling.
        Functionality: This change refines how function declarations are processed, potentially avoiding issues with scope handling.
        Performance: The removal of the redundant parameter could improve the efficiency of function declaration processing, as fewer variables need to be managed.
        Correctness: The change is expected to improve correctness by adhering to the correct scoping rules for function declarations. There is no change to the behavior of the functions themselves.
        Other Considerations: This change contributes to cleaner and more maintainable code by simplifying the function declaration logic.

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

        Provide a detailed technical analysis of the changes made, covering the following areas:
        - Summary of Changes
        - Functionality
        - Performance
        - Correctness
        - Other Considerations

        Do not repeat the prompt.
        {f"Follow this recommendations: {comment}" if comment else ''}

        Summary of Changes:
    """

  prompt = clean_text_paragraph(prompt)
  return prompt


def generate_quality_assurance_prompt(technical_summary):
    """
    Generate the QA prompt based on the technical summary.
    """
    prompt = f"""
    You are a quality assurance expert tasked with evaluating the technical summary of a commit. Below is the technical summary of the changes made in the commit:

    Your task is to evaluate the quality of the technical summary by assigning it a mark from **0 to 10** and providing feedback for improvement. Use the following guidelines for scoring:

    - **10**: The summary is flawless, thoroughly explains all key aspects, and includes exceptional clarity and insight.
    - **8-9**: The summary is clear, detailed, and mostly complete, with minor room for improvement.
    - **6-7**: The summary is adequate but lacks some details, clarity, or key insights.
    - **4-5**: The summary is incomplete or unclear in significant ways, requiring notable improvement.
    - **0-3**: The summary is severely lacking or inaccurate, failing to convey the purpose, impact, or details of the changes.

    Additionally, provide detailed feedback for improvement, regardless of the score. Highlight the strengths of the summary and suggest specific areas for clarification, expansion, or rephrasing.

    Answer Format:
    - Mark: <0-10>
    - Improvement Suggestions: <Provide detailed feedback, focusing on how to improve the summary or what makes it strong.>

    Example 1:
    Technical Summary:
    The commit introduces a refactor to the authentication module, which involves several key changes. Firstly, the `authenticate_user` function has been modified to support multi-factor authentication by adding a new `mfa_token` parameter. This change allows the system to require both a password and an additional MFA token for users to log in, improving security. Additionally, the function now checks the user's `mfa_status` before authentication and raises an error if MFA is required but not provided. This refactor also ensures backward compatibility, as users who do not have MFA enabled will continue to log in with just their password. Finally, related functions in the `user_session` and `security` modules have been updated to handle the new parameter appropriately. The change enhances overall security without sacrificing usability.

    Evaluation:
    - Mark: 9
    - Improvement Suggestions: The summary thoroughly explains the changes made, including the purpose behind adding MFA support and the backward compatibility considerations. It also outlines the modifications to the `user_session` and `security` modules. However, it could be beneficial to mention whether these changes require additional testing or updates to related systems like user management.

    Example 2:
    Technical Summary:
    This commit addresses a bug in the `calculate_total` function, where the system was not properly handling negative price values in the input list. The function previously did not have any validation for negative prices, which caused unexpected behavior when such prices were included in an order. As part of this fix, a new validation check has been added to ensure that all prices are non-negative before performing the calculation. If any negative price is detected, a `ValueError` is raised, and the calculation is aborted. This prevents the system from incorrectly processing orders with invalid prices and ensures that the order calculation remains accurate. This fix improves the integrity and correctness of the order processing system.

    Evaluation:
    - Mark: 7
    - Improvement Suggestions: The summary clearly explains the bug and how the fix prevents negative prices from being processed. It provides sufficient context on why this validation is necessary. However, it would be useful to briefly mention the impact of this fix on the user experience or checkout process. Also, elaborating on why negative prices were allowed in the first place could add more context.

    Example 3:
    Technical Summary:
    In this commit, the user profile creation process was refactored to streamline data handling. The user profile, which previously had separate fields for `settings` and `preferences`, has now been consolidated into a single `preferences` object. This change reduces the complexity of managing user preferences by grouping related data together, improving readability and maintainability. The new `preferences` object holds all settings, such as notification preferences, theme settings, and language preferences, making it easier to handle and update user data. This change is part of an ongoing effort to simplify the codebase and reduce the number of scattered data structures that need to be maintained.

    Evaluation:
    - Mark: 5
    - Improvement Suggestions: While the summary provides a clear explanation of the refactor, it could benefit from more context on how the change will impact the user experience or the way the user profile data is accessed in other parts of the system. The description is missing the rationale behind choosing to combine `settings` and `preferences` into a single object—this would help readers understand why this change is beneficial in the long run.

    Now, please evaluate the provided technical summary. Do not repeat the prompt.

    Technical Summary:
    {technical_summary}

    Answer:
    """
    prompt = clean_text_paragraph(prompt)
    return prompt


def ask_model_technical_analysis(prompt, pipe):
  answer = pipe(
      prompt,
      max_new_tokens= 500,
      do_sample=True,
      top_p = None,
      temperature= 0.7
  )[0]['generated_text']

  answer = answer.split("Summary of Changes:")[-1]
  return answer

def ask_model_quality_assurance(prompt, pipe):
  answer = pipe(
      prompt,
      max_new_tokens=500,  # Increased tokens
      do_sample=True,
      top_p=None,
      temperature=0.7
  )[0]['generated_text']

  answer = answer.split("Answer:")[-1]
  # Extract decision (True/False) and improvement suggestions (comment)
  lines = answer.strip().split("\n")

  # Find the line containing "Mark"
  mark_line = next((line for line in lines if "Mark" in line), None)
  if mark_line is not None:
    mark = mark_line.split(":")[-1].strip()
  else:
    mark = "-1"  # or some default value if not found

  # Find the line containing "Improvement Suggestions"
  improvement_suggestions_line = next((line for line in lines if "Improvement Suggestions" in line), None)
  if improvement_suggestions_line is not None:
    improvement_suggestions = improvement_suggestions_line.split(":")[-1].strip()
  else:
    improvement_suggestions = "No suggestions provided."  # or some default value


  return mark, improvement_suggestions


def generate_technical_report(commit, pipe_llama):
  mark_qa = -1
  improvements = None
  technical_summary= None
  THRESHOLD = 9

  while int(mark_qa) < THRESHOLD:

    prompt = generate_prompt_technical_analysis(commit, improvements)
    technical_summary = ask_model_technical_analysis(prompt, pipe_llama)

    qa_prompt = generate_quality_assurance_prompt(technical_summary)
    mark_qa, improvements = ask_model_quality_assurance(qa_prompt, pipe_llama)

    print(f"Mark: {mark_qa}")
    print(f"Improvement suggestions: {improvements}")

  return technical_summary
