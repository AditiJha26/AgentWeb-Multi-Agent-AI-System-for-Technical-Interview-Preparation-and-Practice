from app.core.context_store import ContextStore
from app.agents.planner_agent import PlannerAgent

if __name__ == "__main__":
    context = ContextStore()
    planner = PlannerAgent(name="planner", context=context)

    user_goal = "I want to get a machine learning internship at Amazon in 4 weeks"
    output = planner.run(user_goal)

    print("\nGenerated Interview Plan:\n")
    print(output)
