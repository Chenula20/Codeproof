# Explanation Evaluation Prompt

Evaluate a user's explanation of code or a concept.

## Criteria
- Accuracy (0.0-1.0): Is the explanation technically correct?
- Coverage (0.0-1.0): Does it cover expected concepts?
- Clarity (0.0-1.0): Is it clear and well-structured?
- Depth (0.0-1.0): Does it show deep understanding?

## Input
- User's explanation text
- Expected concepts to cover
- Reference code/context
- Difficulty level

## Output
- Overall score (0.0-1.0)
- Detailed feedback
- Pass/fail based on threshold