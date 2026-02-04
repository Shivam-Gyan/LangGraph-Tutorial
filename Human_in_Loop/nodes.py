from models import generation_model, structured_parser_model
from states import PostState, EvaluationSchema
from prompts import generation_prompt, evaluation_prompt, optimise_prompt
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import interrupt,Command


# Generation Node
def generation_node(state:PostState):

    # getting the prompt messages for generation
    messages = generation_prompt(state)

    # getting the response from the generation model
    response = generation_model.invoke(messages)

    return {
        "post": response.content,
        "post_history": [response.content],
    }

# Evaluation Node
def evaluation_node(state:PostState):

    # getting the prompt messages for evaluation
    messages = evaluation_prompt(state)

    # getting the response from the evaluation model
    response = structured_parser_model.invoke(messages)

    if response.evaluated_post and response.feedback: # type: ignore
        return {
            "evaluated_post": response.evaluated_post, # type: ignore
            "feedback": response.feedback, # type: ignore
            "feedback_history": [response.feedback] # type: ignore
        }
    else:
        return {
            "evaluated_post": "not_approved",
            "feedback": "The evaluation model did not return a valid response.",
            "feedback_history": ["The evaluation model did not return a valid response."]
        }

# Optimisation Node
def optimise_node(state:PostState):

    messages = optimise_prompt(state)

    response = generation_model.invoke(messages)

    return {
        "post": response.content,
        "post_history": [response.content],
        'iteration': state.iteration + 1,
    }

# Conditional Node 
def conditional_node(state:PostState):
    if state.evaluated_post == "approved":
        return 'approved'
    else:
        if state.iteration < state.max_iteration:
            return 'not_approved'
        else:
            return 'approved'


# publish node
def publish_node(state:PostState):

    decision_message = interrupt(
    {
        "type": "human_approval_request",
        "reason": "Permission required to publish the generated social media post.",
        "instruction": (
            "Review the final generated tweet below and decide whether it is safe, "
            "appropriate, and ready to be published publicly."
        ),
        "post": state.post,
        "expected_format": {
            "approved": "boolean (True if the post can be published, false otherwise)",
            "comments": "string (optional feedback or reason for rejection)"
        }
    }
    )

    return Command(
        update={
            "publish_approval": "approved" if decision_message['approved'] else "not_approved",
            "comments": decision_message.get("comments", "")
        }
    )