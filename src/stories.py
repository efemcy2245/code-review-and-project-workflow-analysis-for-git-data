import re
from utils import clean_text_paragraph


def prompt_story_summary(role, pair):
    """
    Generate a prompt for summarizing a git commit.
    """

    prompt = f"""
    Create a short story where the main character plays the role of a [ROLE]. The character takes the following action: [ACTION].
    The reason for this action is: [REASON/BENEFIT]. The story should be concise, focusing on how the character’s action leads to a positive outcome.

      **Example1**
    **Input**
    performance engineer':
    ('I want to optimize the JavaScript engine by implementing quicksort and heapsort','so that it runs more efficiently in real-world applications.')

    **Output**
    The performance engineer examined the JavaScript engine, looking for ways to boost efficiency. "I want to optimize the engine by implementing quicksort and heapsort," he thought. "This will make it run more efficiently in real-world applications."
    The engine had been functional, but the sorting algorithms it relied on were slowing things down. By adding quicksort for most cases and heapsort for edge cases, the engineer could significantly improve performance.
    After implementing the changes, the engine ran faster and handled larger, more complex tasks with ease. The engineer tested it in real-world scenarios, satisfied that the optimization would make a noticeable difference in everyday applications.


    **Example2**
    **Input**
    'JavaScript developer':
    ('I want to simplify array.prototype.sort by sorting in place without libc','so that I can reduce memory allocations and eliminate the risk of memory leaks.')

    **Output**
    The JavaScript developer looked at the array.prototype.sort function and thought, "I want to simplify this by sorting in place without using libc, so that I can reduce memory
    allocations and eliminate the risk of memory leaks."
    The current sorting method was efficient but relied on external libraries that introduced unnecessary memory usage and potential leaks.
    By sorting in place, the developer could eliminate this risk and improve overall performance.
    After modifying the implementation, the developer tested it with various data sets. The results were clear: memory usage was reduced,
    and the system ran more efficiently. The developer smiled, knowing the change would make the codebase more reliable.

    **Example3**
    'project manager':
    ('I want to ensure that the changes in utf.h align with the project goals of improving code readability and supporting Unicode', 'so that the codebase is more maintainable and scalable.')

    **Output**
    The project manager gathered the team for a quick meeting. "I want to prioritize the maintenance of the compiler's behavior over performance considerations," he explained. "This will help align with our long-term goals."
    The team had been discussing optimizations that could speed up the compiler, but the manager knew that stability and predictability were more important for the project’s future. By focusing on maintaining consistent behavior, they could ensure that the compiler would remain reliable as new features were added.
    With the direction set, the team agreed to focus on the long-term vision, knowing that performance improvements could always come later without compromising the compiler's core functionality.

    Follow the above examples to extract user stories from similar technical descriptions, don't repeat the previous examples.
    Generate only the output.
    ---
    **Example4**

    # **Input:**
    '{role}':
    ({pair})

    **Output:**
    """
    prompt = clean_text_paragraph(prompt)
    return prompt


def prompt_story_summary_tech(role, pair):
    """
    Generate a prompt for summarizing a git commit.
    """

    prompt = f"""
    Create a short story where the main character plays the role of a [ROLE]. The character takes the following action: [ACTION].
    The reason for this action is: [REASON/BENEFIT]. The story should be concise, focusing on how the character’s action leads to a positive outcome.

    **Example1**
    **Input**
    'developer':
    ('I want to refactor the quicksort implementation to use heapsort,','so that it becomes more efficient and scalable for various scenarios.')

    **Output**
     The developer stared at the quicksort implementation, knowing it had its limits. "I want to refactor the quicksort implementation to use heapsort," he said.
     "This will make it more efficient and scalable for various scenarios. "Quicksort had worked fine for most cases, but in extreme scenarios, its performance faltered.
     Heapsort, with its consistent time complexity and low memory usage, would solve these issues. He quickly refactored the code, replacing quicksort with heapsort.
     The system now handled large datasets with ease, running faster and using less memory. The developer smiled, satisfied with the improvements, knowing that the
     change would make the system ready for anything.


    **Example2**
    **Input**
    'software architect':
    ('I want to implement a simple quicksort for small fragments in jsgc.c', 'so that it can be used as a replacement for qsort.')

    **Output**
    The software architect reviewed the code in jsgc.c and muttered to himself, "I want to implement a simple quicksort for small fragments here, so that it can be used as a replacement for qsort."
    He knew qsort was effective, but it came with overhead that wasn't necessary for small data sets. A simpler, more efficient quicksort would improve the system's performance by
    reducing unnecessary complexity. With a few keystrokes, he crafted a streamlined quicksort, tailored for small fragments. The change was small, but it made a big difference:
    the new quicksort sped up processing without the overhead of qsort. The architect tested the system, and the results were clear—performance had improved.

    **Example3**
    'project manager':
    ('I want to ensure that the changes in utf.h align with the project goals of improving code readability and supporting Unicode', 'so that the codebase is more maintainable and scalable.')

    **Output**
    The project manager reviewed the changes in utf.h and said, "I want to ensure that these changes align with our project goals of improving code readability and supporting Unicode,
    so that the codebase is more maintainable and scalable." The manager knew that improving readability would help current and future developers navigate the code with ease,
    while ensuring full Unicode support would make the system adaptable to a broader range of languages and characters. With the team aligned on these goals, the changes were carefully
    implemented, making the codebase cleaner, more flexible, and ready for future growth. The manager felt confident knowing the project was on the right track for long-term success.

    Follow the above examples to extract user stories from similar technical descriptions, don't repeat the previous examples.
    Generate only the output.
    ---
    **Example4**

    # **Input:**
    '{role}':
    {pair}

    **Output:**
    """
    prompt = clean_text_paragraph(prompt)
    return prompt


def create_role_dict(user_stories):                #### we do not consider the lines without so that
    role_dict = {}
    line = user_stories.split("\n")
    for story in line:
          try:                                     ### if the row is not set properly is discarded
            role = remove_stars(story.split(" : ")[0].strip())
            action_benefit = story.split(" : ")[1].strip()
            action = action_benefit.split(" so that ")[0].strip()
            benefit = action_benefit.split(" so that ")[1].strip()
            if role not in role_dict:
                role_dict[role] = []

            role_dict[role].append((f"I want {action}", f"so that {benefit}"))

          except IndexError as e:
            continue
    return role_dict


def ask_model_final_user_story(prompt, pipe):
    """
    Ask the model to summarize a git commit.
    """
    answer = pipe(
        prompt,
        max_new_tokens=5000,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )[0]['generated_text']

    answer = answer.split("**Output:**")[-1]
    return answer


##### USING MORE EXAMPLE IS MISSLEADING FOR THE MODEL
def create_compound_story_prompt(actor, story1, story2):
    prompt = f"""
        **Instruction**
        Combine the key points from both stories into a **single, cohesive narrative**. Focus on highlighting the roles and contributions of the characters involved, ensuring that their efforts are logically connected and complement each other. Emphasize collaboration and the impact of their work on the overall success of the project.
        - Keep the narrative concise and precise.
        - Avoid repeating ideas or sentences.
        - Ensure a smooth flow, maintaining clarity and engagement throughout.

        **Example 1**
        **Input**
        Actor: developer
        Story 1: The developer examined the implementation of array.prototype.sort. "I want to simplify this by removing the libc dependency and implementing a simple quicksort with insertion sort for small fragments," he thought. "This will improve performance."
        The current sorting method was efficient but relied on external libraries that introduced unnecessary memory usage and potential leaks.
        By simplifying the implementation, the developer could eliminate this risk and improve overall performance.
        After modifying the code, the developer tested it with various data sets. The results showed significant improvements in performance. The developer was satisfied that the changes would make the codebase more reliable.
        Story 2: The UX designer reviewed the new UI element designs and thought, "I want to ensure that the visual design aligns with the project's brand guidelines."
        The designer had been tasked with creating the new UI elements, but the project's brand guidelines were still being finalized. By focusing on ensuring consistency with the guidelines, the designer could create visually appealing and cohesive designs.
        After reviewing the designs, the designer made adjustments to ensure that the new UI elements aligned with the brand guidelines. The result was a cohesive and consistent visual design that met the project's standards.

        **Output**
        The developer examined the implementation of array.prototype.sort with a clear goal: "I want to simplify this by removing the libc dependency and implementing a quicksort with insertion sort for small fragments." Simplifying the method would reduce memory usage and eliminate potential risks from external libraries.
        After refactoring the code, the developer tested it extensively with various datasets. The results showed improved performance and reliability, confirming the changes were effective.
        Just as the UX designer refined UI elements to align with brand guidelines, the developer’s meticulous work ensured the sorting method was both efficient and dependable, contributing to a more robust codebase.

        **Example 2**
        **Input**
        Actor: tester
        Story 1: The manager evaluated the new sorting algorithm, considering its cost-effectiveness and scalability. "I want to ensure that it meets the project's budget and resource requirements," he thought. "This will help us allocate resources efficiently and make informed decisions."
        The manager analyzed the algorithm's performance and cost-benefit analysis, searching for opportunities to optimize its resource usage. By verifying the algorithm's cost-effectiveness, the manager could identify potential issues that could compromise the project's budget and resource allocation.
        With the cost-benefit analysis complete, the manager reported back to the developers, highlighting the need for further optimization to meet the project's specific requirements.
        Story 2: The tester looked at the `split` method and thought, "I want to validate this behavior by testing it with empty input strings."
        The current implementation had been working fine, but the tester knew that edge cases could lead to unexpected results.
        To test the method, the tester created test cases with empty strings and verified that the function returned the expected results. With this validation, the tester could ensure that the `split` method was working correctly.
        After implementing the test, the tester tested the method with various input scenarios. The results were clear: the `split` method returned the correct results in all cases.
        The tester was satisfied that the validation would help improve the method's reliability.

        **Output**
        The tester, aware of the manager's focus on cost-effectiveness and scalability for the sorting algorithm, turned their attention to validating the split method. "I need to ensure this works with all inputs," they thought, considering edge cases like empty strings.
        They quickly created test cases, focusing on scenarios that might cause errors, and ran them. The method passed each one flawlessly, confirming its reliability.
        Just as the manager optimized the algorithm’s resources, the tester optimized for precision, ensuring the method would perform smoothly across all scenarios, contributing to the project's success.

        **Example 3**
        **Input**
        Actor: end-user
        Story 1: The manager gathered the team for a meeting. "I want the development time to be reduced," he said. "This will enable us to implement and test new features more quickly." The team discussed the challenges of implementing new features, but the manager knew that speed was essential.
        By introducing more efficient development processes and tools, the manager could ensure that new features were implemented and tested faster, without compromising quality. With the direction set, the team agreed to focus on implementing the new features, knowing that speed would be crucial in the future.
        Story 2: The quality assurance engineer wanted to implement the filter method with correct edge cases, ensuring it works as expected in various scenarios.

        **Output**
        The manager gathered the team for a meeting. "I want the development time to be reduced," he said. "This will enable us to implement and test new features more quickly." The team discussed the challenges of balancing speed and quality, but the manager was resolute. He knew that in order to stay competitive, they had to move faster without compromising the integrity of their work.
        At the same time, the quality assurance engineer was working hard on implementing the filter method. She understood how important it was to cover all edge cases, ensuring it worked as expected across a variety of scenarios. She was meticulous, knowing that testing thoroughly would save time in the long run by preventing bugs from slipping through.
        As the manager continued to push for faster development, the engineer made sure to focus on detail and accuracy in her work. Together, their collaboration allowed the team to meet the challenge—implementing new features quickly while maintaining high standards.

        **Input**
        Actor: {actor}
        Story 1: {story1}
        Story 2: {story2}

        **Output**
        Create a unified, engaging story that combines the key elements of both inputs into one cohesive narrative. Avoid unnecessary details or filler content, ensuring the final output is clear and impactful.\n"""

    prompt = clean_text_paragraph(prompt)
    return prompt


def create_compound_story_prompt(actor, story1, story2):
    prompt = f"""
        **Instruction**
        Combine the key points from both stories into a **single, cohesive narrative**. Focus on highlighting the roles and contributions of the characters involved, ensuring that their efforts are logically connected and complement each other. Emphasize collaboration and the impact of their work on the overall success of the project.
        - Keep the narrative concise and precise.
        - Avoid repeating ideas or sentences.
        - Ensure a smooth flow, maintaining clarity and engagement throughout.

        **Example 1**
        **Input**
        Actor: developer
        Story 1: The developer examined the implementation of array.prototype.sort. "I want to simplify this by removing the libc dependency and implementing a simple quicksort with insertion sort for small fragments," he thought. "This will improve performance."
        The current sorting method was efficient but relied on external libraries that introduced unnecessary memory usage and potential leaks.
        By simplifying the implementation, the developer could eliminate this risk and improve overall performance.
        After modifying the code, the developer tested it with various data sets. The results showed significant improvements in performance. The developer was satisfied that the changes would make the codebase more reliable.
        Story 2: The UX designer reviewed the new UI element designs and thought, "I want to ensure that the visual design aligns with the project's brand guidelines."
        The designer had been tasked with creating the new UI elements, but the project's brand guidelines were still being finalized. By focusing on ensuring consistency with the guidelines, the designer could create visually appealing and cohesive designs.
        After reviewing the designs, the designer made adjustments to ensure that the new UI elements aligned with the brand guidelines. The result was a cohesive and consistent visual design that met the project's standards.

        **Output**
        The developer examined the implementation of array.prototype.sort with a clear goal: "I want to simplify this by removing the libc dependency and implementing a quicksort with insertion sort for small fragments." Simplifying the method would reduce memory usage and eliminate potential risks from external libraries.
        After refactoring the code, the developer tested it extensively with various datasets. The results showed improved performance and reliability, confirming the changes were effective.
        Just as the UX designer refined UI elements to align with brand guidelines, the developer’s meticulous work ensured the sorting method was both efficient and dependable, contributing to a more robust codebase.

        **Input**
        Actor: {actor}
        Story 1: {story1}
        Story 2: {story2}

        **Output**
        Create a unified, engaging story that combines the key elements of both inputs into one cohesive narrative. Avoid unnecessary details or filler content, ensuring the final output is clear and impactful.\n"""

    prompt = clean_text_paragraph(prompt)
    return prompt

def remove_stars(input_string):
    """
    Removes all asterisk (*) characters from the given string.

    Parameters:
        input_string (str): The string to process.

    Returns:
        str: The string without any asterisk characters.
    """
    return input_string.replace('*', '')