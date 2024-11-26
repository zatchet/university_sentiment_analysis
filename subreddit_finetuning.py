import os
from openai import OpenAI
import pandas as pd
from tqdm import tqdm

# initializing openai configuration
BASE_URL = "http://199.94.61.113:8000/v1/" # os.getenv('CS4973_BASE_URL')
API_KEY=api_key = "bengani.k@northeastern.edu:8H4rX1jbx2FxmFQzOXev" # os.getenv('CS4973_API_KEY')
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# initializing system prompt for question generation
SYSTEM_PROMPT = '''
Come up with a hypothetical question that would be relevant to the university given. 
Return only the question. Be sure to include the name of the university in the question.

Examples:
Question: Boston Univeristy
Answer: How do people feel about the dorms at Boston University?
Question: University of Washington
Answer: At the University of Washington, do people like the quality of the food?
'''

# convert college subreddits csv to dataframe
df = pd.read_csv('csv_files/college_subreddits.csv')
df.drop(columns=['location'], inplace=True)


def generate_for_benchmark():
    # generating 1 question per college subreddit
    benchmark_df = pd.DataFrame(columns=['subreddit', 'question'])
    for index, row in df.iterrows():
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.append({'role': 'user', 'content': row['name']})

        resp = client.chat.completions.create(
            messages = messages,
            model = "meta-llama/Meta-Llama-3.1-8B-Instruct",
            temperature=0.9,
            max_tokens=500,
        )
        resp = resp.choices[0].message.content
        benchmark_df.loc[len(benchmark_df)] = {'subreddit': row['subreddit'], 'question': resp}
        
    # post-processing of questions and saving to file
    benchmark_df.drop_duplicates(subset=['question'], inplace=True)
    benchmark_df.to_csv('csv_files/subreddit_finetuning_benchmark.csv', index=False)
    
    return benchmark_df


def generate_for_finetuning():
    # generating 5 questions per college subreddit
    questions_df = pd.DataFrame(columns=['subreddit', 'question'])
    for index, row in tqdm(df.iterrows()):
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.append({'role': 'user', 'content': row['name']})

        for _ in range(5):
            resp = client.chat.completions.create(
                messages = messages,
                model = "meta-llama/Meta-Llama-3.1-8B-Instruct",
                temperature=0.9,
                max_tokens=500,
            )
            resp = resp.choices[0].message.content
            questions_df.loc[len(questions_df)] = {'subreddit': row['subreddit'], 'question': resp}

    # post-processing of questions and saving to file
    questions_df.drop_duplicates(subset=['question'], inplace=True)
    questions_df.to_csv('csv_files/subreddit_finetuning_questions.csv', index=False)
    
    return question_df