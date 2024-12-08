import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import SystemMessage
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from typing import Dict
import re
import json
from api_config import OPENAI_API_KEY  # Import the API key


# Check if the API key is set
if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key":
    raise ValueError("Please set your OpenAI API Key in the api_config.py file.")

# Set the API key in the environment variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# Global dictionary to store results
results = {}
# Questions
question1 = "What are the main technical concepts discussed in this article?"
question2 = "What are the key findings or advancements mentioned?"
question3 = "What potential impacts or applications are discussed?"
# Global variable for the QA chain
qa_chain = None

# Initialize LLM once for reuse
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini",)

def create_vectorstore(text: str) -> FAISS:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    texts = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(texts, embeddings)

def answer_question1():
    global results
    global qa_chain
    results[question1] = qa_chain.run(question1)

def answer_question2():
    global results
    global qa_chain
    results[question2] = qa_chain.run(question2)

def answer_question3():
    global results
    global qa_chain
    results[question3] = qa_chain.run(question3)

def extract_key_info(article: str) -> dict:
    global qa_chain
    vectorstore = create_vectorstore(article)
    retriever = vectorstore.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    import threading

    # Create threads for each function
    t1 = threading.Thread(target=answer_question1)
    t2 = threading.Thread(target=answer_question2)
    t3 = threading.Thread(target=answer_question3)

    # Start the threads
    t1.start()
    t2.start()
    t3.start()

    # Wait for all threads to complete
    t1.join()
    t2.join()
    t3.join()

    return results


def generate_summary(article: str, key_info: dict) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert in summarizing technical news articles. Your task is to create a concise and structured summary of the given article, focusing on the key technical information."),
        HumanMessagePromptTemplate.from_template("""
Article: {article}

Key Information:
{key_info}

Please provide a structured summary of this article, following these guidelines:

   a. Focus on the actual title for the article and then adjust it to start with a noun or an entity relevant to the news.
   b. Then, provide a summary that:
      - First Sentence: Describes what was developed or achieved.
      - Second Sentence: Briefly explains the functionality or purpose of the development.
      - Third Sentence: Mentions key results or findings.
      - Fourth Sentence: Provides any future plans or goals related to the development.
   c. Keep the summary under 110 words, excluding the category and the title.
   d. Focus on clarity and conciseness.
   e. Focus on the important number and mention it if it is important..
Format your response as follows:
                                                                                                  
[Title]

                                                                                          
[Four-sentence summary]

                                       
Do not include any labels like "Title:" or "Summary:". Start directly with the title, followed by a line break, and then, with the summary.
                                       
""")
    ])
    llm_summary = ChatOpenAI(model_name="gpt-4o-mini")
    chain = LLMChain(llm=llm_summary, prompt=prompt)
    return chain.run(article=article, key_info=str(key_info))

def translate_to_arabic(text: str) -> str:
    prompt_s = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert translator specializing in technical translations from English to Arabic. Your task is to provide an accurate and fluent translation that preserves the technical nuances and structure of the original text."),
        HumanMessagePromptTemplate.from_template(text)
    ])
    Fine_tunes_llm = ChatOpenAI(model_name="ft:gpt-4o-mini-2024-07-18:personal:translate:AHmy4few")
    chain = LLMChain(llm=Fine_tunes_llm, prompt=prompt_s)
    return chain.run(text=text)


def clean_json_output(output):
    # Use a regular expression to find the JSON array in the output
    json_match = re.search(r'\[\s*{.*?}\s*\]', output, re.DOTALL)
    if json_match:
        return json_match.group(0)  # Extract the JSON array
    return output  # Return the output as is if no JSON is found

def match_summary_with_article(article: str, summary: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are tasked with analyzing an article and its summary. Your goal is to identify and match each sentence in the summary with the corresponding sentence(s) in the article. The matching sentence(s) may be identical or convey the same meaning, even if rephrased. Provide an output where each sentence from the summary is mapped to one or more corresponding sentences from the article."),
        HumanMessagePromptTemplate.from_template("""
Instruction:
Provide the output strictly as a JSON array. Do not include any additional text or explanations. Each object in the JSON array should have the following fields:

- "summary_sentence": The exact text of the summary sentence.
- "article_sentences": An array containing one or more sentences from the article that correspond to the summary sentence.

Ensure that the output is valid JSON and contains no extra characters or formatting outside of the array.
the Summary:
{summary}/n/n

Article:
{article}                                                                                  
""")
    ])

    llm_h = ChatOpenAI(model_name="gpt-4o")
    chain = LLMChain(llm=llm_h, prompt=prompt)

    # Pass the inputs correctly and get the output
    output = chain.run(article=article, summary=summary)

    # Clean the output to extract the JSON array
    cleaned_output = clean_json_output(output)
    try:
        parsed_output = json.loads(cleaned_output)  # Parse the cleaned JSON string
        return json.dumps(parsed_output)  # Return the validated and cleaned JSON string
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON returned by LLM.")
        print("Raw Output:", output)  # Log the raw output for debugging
        return output  # Return the raw output if it's not valid JSON