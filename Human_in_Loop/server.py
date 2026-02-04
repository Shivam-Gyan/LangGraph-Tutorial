
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command
from states import PostState
from nodes import conditional_node, evaluation_node, generation_node, optimise_node, publish_node, publish_node
from langgraph.checkpoint.memory import InMemorySaver
from configuration import config # importing configuration settings from external file
from pprint import pprint

# graph structure

# 1. initialize the graph with the initial state
graph  = StateGraph(PostState)

# 2. add nodes to the graph
graph.add_node("generation", generation_node)
graph.add_node("evaluation", evaluation_node)
graph.add_node('optimised_evaluation', optimise_node)  # Reusing evaluation_node for optimized evaluation
graph.add_node('publish_node',publish_node)

# 3. define the edges and flow
graph.add_edge(START, "generation")
graph.add_edge("generation", "evaluation")
graph.add_conditional_edges("evaluation", conditional_node ,{
    'approved': 'publish_node',
    'not_approved': 'optimised_evaluation'
})
graph.add_edge("optimised_evaluation", "evaluation")
graph.add_edge("publish_node", END)

# 4. setup checkpointer
checkpointer = InMemorySaver()

# 5.Compile the graph

post_generation_Workflow = graph.compile(checkpointer=checkpointer)

# 6. execute the graph
if __name__ == "__main__":

    initial_state = PostState(
        title="The struggles of working from home",
        post="",
        post_history=[],
        feedback_history=[],
        evaluated_post="not_approved",
        feedback="",
        iteration=0,
        max_iteration=3,
        # messages=[]
        publish_approval="not_published",
        comments=""
    )

    final_state = post_generation_Workflow.invoke(initial_state, config=config) # type: ignore
    # print("\n\n\n\nFinal State:\n\n", final_state)

    snapshot = post_generation_Workflow.get_state(config=config) # type: ignore

    if snapshot.next:
        print("\n\n\n\nSnapshot State:", snapshot.next)

        interrupt_data = snapshot.interrupts[0].value

        print("\n\n🔔 HUMAN APPROVAL REQUIRED")
        print("-" * 50)
        print("Reason:", interrupt_data["reason"])
        print("\nInstruction:", interrupt_data["instruction"])
        print("\nGenerated Post:\n")
        print(interrupt_data["post"])
        print("-" * 50)

        user_approval = input("Approve this post? (y/n): ").strip().lower()
        user_comment = input("Any comments (optional): ").strip()

        user_input = {
            "approved": True if user_approval == 'y' else False,
            "comments": user_comment
        }

        # print()
        final_result = post_generation_Workflow.invoke(
            Command(resume=user_input),
            config=config # type: ignore
        )

        # print("\n\n\n\nFinal Result State:\n\n", final_result)
        print("\n\n")
        # printable_state = {
        #     "title": final_result.title,
        #     "post": final_result.post,
        #     # "post_history": final_result.post_history,
        #     # "feedback_history": final_result.feedback_history,
        #     "evaluated_post": final_result.evaluated_post,
        #     "feedback": final_result.feedback,
        #     "iteration": final_result.iteration,
        #     "publish_approval": final_result.publish_approval,
        #     "comments": final_result.comments
        # }
        pprint(final_result)
        print("\n\n")


    else:
        print("\n\n\n\nNo Snapshot Available")

