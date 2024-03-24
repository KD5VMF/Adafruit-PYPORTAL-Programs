import time
import board
import displayio
from adafruit_display_text import label
import terminalio
import random

# Function to create a matrix of dimensions 4x4 with random integers
def create_matrix_4x4(max_value=150):
    return [[random.randint(1, max_value) for _ in range(4)] for _ in range(4)]

# Function to multiply two matrices
def multiply_matrices(A, B):
    # Resultant matrix of zeros
    result = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]
    return result

# Convert matrix to string for display
def matrix_to_string(matrix):
    return '\n'.join([' '.join(map(str, row)) for row in matrix])

# Display setup
display = board.DISPLAY
while True:
    # Clear display
    display.show(displayio.Group())

    # Create two 4x4 matrices
    A = create_matrix_4x4()
    B = create_matrix_4x4()

    # Multiply matrices
    result = multiply_matrices(A, B)

    # Text setup for display
    matrix_a_text = "Matrix A:\n" + matrix_to_string(A)
    matrix_b_text = "Matrix B:\n" + matrix_to_string(B)
    result_text = "Result:\n" + matrix_to_string(result)

    # Combine all text
    all_text = matrix_a_text + "\n\n" + matrix_b_text + "\n\n" + result_text

    # Create label
    text_area = label.Label(terminalio.FONT, text=all_text, color=0x00FF00)
    text_group = displayio.Group(scale=1, x=8, y=8)  # Adjust scale and position as needed
    text_group.append(text_area)

    # Show on display
    display.show(text_group)

    # Refresh display and wait
    time.sleep(5)
