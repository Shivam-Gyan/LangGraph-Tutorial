
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel,Field
from typing import Annotated, List, Literal
import operator


class PostState(BaseModel):
    title: str = Field(...,description="title of post you want to create?")
    post: str = Field(..., description="generated post by LLM model ")

    post_history: Annotated[List[str],operator.add, Field(..., description="Collection of all post generated throughout the process")]
    feedback_history: Annotated[List[str],operator.add, Field(..., description="Collection of all feedback generated throughout the process")]

    evaluated_post: Literal["approved", "not_approved"] = Field(..., description="Evaluation of the generated post")
    feedback: str = Field(..., description="Feedback for improving the post if not approved")

    iteration: int = Field(..., description = "No. of iteration it goes through out the execution")
    max_iteration: int  = Field(..., description="")

    # messages: Annotated[List[BaseMessage], add_messages, Field(..., description="Messages exchanged with the LLM models during the process")]
    
    publish_approval: Literal["published", "not_published"] = Field("not_published", description="Status of the post publication")
    comments: str = Field("", description="Comments on the published post")


class EvaluationSchema(BaseModel):
    evaluated_post: Literal["approved", "not_approved"] = Field(..., description="Evaluation of the generated post")
    feedback: str = Field(..., description="Feedback for improving the post if not approved")

