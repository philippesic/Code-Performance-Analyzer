#Comparing our model's ouput with DeepSeek's output to measure accuracy.

import difflib

def compare_model_accuracy():
    #Try to read both of the files which is our model's output and DeepSeek output
    try:
        #Read our model's output from file
        with open('our_model_output.txt', 'r', encoding='utf-8') as f:
            our_outputs = [line.strip() for line in f if line.strip()]

        #Read DeepSeek's output from file
        with open('deepseek_output.txt', 'r', encoding='utf-8') as f:
            deepseek_outputs = [line.strip() for line in f if line.strip()]
   
    except FileNotFoundError as e:
        #If file not found, print error message.
        print(f" File Error: {e}")
        print("\n Please make sure both files exist:")
        print(" - our_model_output.txt (our model's output)")
        print(" - deepseek_output.txt (DeepSeek's output)")
        return

    # Compare as many examples as we have in both files
    if len(our_outputs) != len(deepseek_outputs):
        print(f"Warning: Files have different lengths ({len(our_outputs)} vs {len(deepseek_outputs)})")
        min_len = min(len(our_outputs), len(deepseek_outputs))
        our_outputs = our_outputs[:min_len]
        deepseek_outputs = deepseek_outputs[:min_len]
        print(f"Using first {min_len} examples from both files\n")
    else:
        print(f"Comparing {len(our_outputs)} examples from both files\n")

    #Counting the number of examples that we are comparing
    total = len(our_outputs)

    exact_matches = 0
    close_matches = 0
    different_outputs = 0

    #Comparing each example one by one
    for i in range(total):
        our_answer = our_outputs[i]
        deepseek_answer = deepseek_outputs[i]

        #Check for exact match in the answers
        if our_answer == deepseek_answer:
            exact_matches = exact_matches + 1
            print(f"Example {i+1}: Exact Match")
        else:
            # Calculate how similar the answers are (0% to 100%)
            similarity = difflib.SequenceMatcher(None, our_answer, deepseek_answer).ratio()

            # If answers are 80% or more similar, count as "close match"
            if similarity >= 0.8:
                close_matches = close_matches + 1
                print(f"Example {i+1}: Close Match ({similarity:.0%} similar)")
            
            # If answers are less than 80% similar, count as different
            else:
                different_outputs = different_outputs + 1
                print(f"Example {i+1}: Different Outputs ({similarity:.0%} similar)")
                print(f"  Our model: {our_answer[:80]}...")
                print(f"  DeepSeek:  {deepseek_answer[:80]}...")
    
    #Calculating the accuracy percentages
    exact_accuracy = (exact_matches / total) * 100
    close_accuracy = ((close_matches + exact_matches) / total) * 100

   
    #Displaying the final results
    print()
    print("=" * 50)
    print("ACCURACY RESULTS")
    print("=" * 50)
    print(f"Total examples compared: {total}")
    print()
    print(f"Exact matches: {exact_matches} ({exact_accuracy:.1f}%)")
    print(f"Close matches: {close_matches} ({close_accuracy:.1f}%)")
    print(f"Different: {different_outputs}")
    print()
    print(f"EXACT ACCURACY: {exact_accuracy:.1f}%")
    print(f"CLOSE+EXACT ACCURACY: {close_accuracy:.1f}%")
    print()

    
    # Give a simple rating and accuracy based on how accurate our model is
    if exact_accuracy >= 90:
        rating = f"Excellent ({exact_accuracy:.1f}%)"
    elif exact_accuracy >= 80:
        rating = f"Good ({exact_accuracy:.1f}%)"
    elif exact_accuracy >= 70:
        rating = f"Fair ({exact_accuracy:.1f}%)"
    else:
        rating = f"Needs Improvement ({exact_accuracy:.1f}%)"
    
    print(f"Overall Rating: {rating}")
    print("=" * 50)
    
#Main Function
if __name__ == "__main__":
    compare_model_accuracy()