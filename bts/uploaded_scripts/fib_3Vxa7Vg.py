# Function to calculate Fibonacci series
def fibonacci(n):
    # Handling edge cases for n <= 0
    if n <= 0:
        return "Input should be a positive integer."
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    # Initialize the first two numbers of the series
    fib_series = [0, 1]
    
    # Calculate the rest of the series
    for i in range(2, n):
        next_num = fib_series[i - 1] + fib_series[i - 2]
        fib_series.append(next_num)
    
    return fib_series

# Test the function
try:
num_terms = int(input("Enter the number of terms in the Fibonacci series: "))
if num_terms <= 0:
    print("Please enter a positive integer.")
else:
    result = fibonacci(num_terms)
    print("Fibonacci Series:", result)
except ValueError:
    print("Invalid input! Please enter an integer.")
