#Replaces time.sleep and utime with async.sleep for code given as a string
def add_async_sleep(code_str, sleep_duration=0.1):
    """
    Adds `await asyncio.sleep(sleep_duration)` before each occurrence of `time.sleep`.
    
    Args:
        code_str (str): The code string to modify.
        sleep_duration (float): The duration for `asyncio.sleep`. Defaults to 0.1 seconds.

    Returns:
        str: The modified code with `await asyncio.sleep` added.
    """
    import asyncio

    # Ensure asyncio is imported
    if 'import asyncio' not in code_str:
        code_str = 'import asyncio\n' + code_str

    # Split the code into lines
    lines = code_str.splitlines()
    new_lines = []

    # Replace `time.sleep` and `utime.sleep` correctly
    for line in lines:
        new_line = line
        # Check for exact matches of `time.sleep` and `utime.sleep`
        if 'time.sleep' in line or 'utime.sleep' in line:
            for time_to_replace in ['time.sleep', 'utime.sleep']:
                if time_to_replace in line:
                    # Replace `time_to_replace` with `await asyncio.sleep` considering arguments
                    before_sleep, after_sleep = line.split(time_to_replace, 1)
                    if '(' in after_sleep and ')' in after_sleep:
                        args = after_sleep.split('(', 1)[1].split(')', 1)[0]
                        new_line = f'{before_sleep}await asyncio.sleep({args})'
                    else:
                        new_line = f'{before_sleep}await asyncio.sleep({sleep_duration})'  # Default duration
                    print("New_line:", new_line)
        print("New_line2:", new_line)
        new_lines.append(new_line)

    # Join the lines back into a single string
    modified_code = '\n'.join(new_lines)
    
    return modified_code

# Example usage
if __name__ == "__main__":
    example_code = """
import time

def example_function():
    print("Starting...")
    time.sleep(1)
    print("Finished sleeping")
    time.sleep(2)
    time.sleep_ms(2000)
"""

    modified_code = add_async_sleep(example_code)
    print("Modified Code:\n", modified_code)

