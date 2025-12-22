"""
Example functions for testing the performance test generator.
These functions demonstrate different time complexities.
"""


def linear_search(arr, target):
    """
    Linear search algorithm.
    Time Complexity: O(n)
    """
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1


def binary_search(arr, target):
    """
    Binary search algorithm (requires sorted array).
    Time Complexity: O(log n)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def bubble_sort(arr):
    """
    Bubble sort algorithm.
    Time Complexity: O(n²)
    """
    n = len(arr)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    return arr


def merge_sort(arr):
    """
    Merge sort algorithm.
    Time Complexity: O(n log n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left, right):
    """Helper function for merge sort."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def fibonacci(n):
    """
    Recursive fibonacci (inefficient).
    Time Complexity: O(2^n)
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_dp(n):
    """
    Dynamic programming fibonacci.
    Time Complexity: O(n)
    """
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]


def matrix_multiply(A, B):
    """
    Naive matrix multiplication.
    Time Complexity: O(n³)
    """
    n = len(A)
    result = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    
    return result


def find_duplicates(arr):
    """
    Find duplicates in an array using set.
    Time Complexity: O(n)
    """
    seen = set()
    duplicates = []
    
    for num in arr:
        if num in seen:
            duplicates.append(num)
        else:
            seen.add(num)
    
    return duplicates


def is_prime(n):
    """
    Check if a number is prime.
    Time Complexity: O(√n)
    """
    if n < 2:
        return False
    
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    
    return True


def constant_time_access(arr, index):
    """
    Access element by index.
    Time Complexity: O(1)
    """
    return arr[index] if 0 <= index < len(arr) else None

