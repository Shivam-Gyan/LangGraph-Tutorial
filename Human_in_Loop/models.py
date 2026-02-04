from langchain_ollama import ChatOllama
from states import EvaluationSchema


# model = ChatOllama(model="ministral-3:3b") # for generation
# model = ChatOllama(model="deepseek-r1:1.5b") # for generation
# model = ChatOllama(model="qwen3:1.7b") # for evaluation

# LLM Model defining --------------------------------------------------------------------------

# 1. evaluation model
eval_model = ChatOllama(model="qwen3:1.7b") # for evaluation
structured_parser_model = eval_model.with_structured_output(EvaluationSchema) 

# 2. Generation Model
generation_model = ChatOllama(model="ministral-3:3b") # for generation
# generation_model = ChatOllama(model="deepseek-r1:1.5b") # for generation
