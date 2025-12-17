import os
import operator
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# --- 1. Define State ---
class GraphState(TypedDict):
    code: str
    # 'operator.add' ensures parallel updates are appended to the list
    reviews: Annotated[List[str], operator.add] 
    final_report: str

# --- 2. Initialize LLM ---
# Ensure GROQ_API_KEY is in your .env file
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. Define Node Functions (Agents) ---

def time_complexity_agent(state: GraphState):
    print("---Analyzing Time Complexity---")
    code = state["code"]
    prompt = ChatPromptTemplate.from_template(
        "Analyze the following C++ code ONLY for **Time Complexity**. "
        "Identify the Big-O notation for the worst-case scenario. "
        "Explain the reasoning (loops, recursion depth, API calls). "
        "Be concise.\n\nCode:\n{code}"
    )
    chain = prompt | llm
    response = chain.invoke({"code": code})
    return {"reviews": [f"⏱️ **Time Complexity:**\n{response.content}"]}

def space_complexity_agent(state: GraphState):
    print("---Analyzing Space Complexity---")
    code = state["code"]
    prompt = ChatPromptTemplate.from_template(
        "Analyze the following C++ code ONLY for **Space Complexity**. "
        "Identify the Big-O notation for memory usage. "
        "Look for: Auxiliary arrays, recursion stack depth, and dynamic memory allocations. "
        "Be concise.\n\nCode:\n{code}"
    )
    chain = prompt | llm
    response = chain.invoke({"code": code})
    return {"reviews": [f"💾 **Space Complexity:**\n{response.content}"]}

def readability_agent(state: GraphState):
    print("---Analyzing Readability---")
    code = state["code"]
    prompt = ChatPromptTemplate.from_template(
        "Analyze the following C++ code ONLY for **Readability & Maintainability**. "
        "Check: Variable naming, indentation, modularity, comments, and modern C++ best practices. "
        "Be concise.\n\nCode:\n{code}"
    )
    chain = prompt | llm
    response = chain.invoke({"code": code})
    return {"reviews": [f"👀 **Readability:**\n{response.content}"]}

def synthesizer_agent(state: GraphState):
    print("---Synthesizing Final Report---")
    reviews = "\n\n".join(state["reviews"])
    code = state["code"]
    prompt = ChatPromptTemplate.from_template(
        "You are a Competitive Programming Coach. Review the C++ code and the analysis reports below.\n"
        "1. Summarize the Time and Space efficiency.\n"
        "2. Provide a **Final Score out of 10** based on efficiency and code quality.\n"
        "3. Provide the improved C++ code if the score is less than 10.\n\n"
        "Original Code:\n{code}\n\n"
        "Analysis Reports:\n{reviews}"
    )
    chain = prompt | llm
    response = chain.invoke({"code": code, "reviews": reviews})
    return {"final_report": response.content}

# --- 4. Build the Graph ---
workflow = StateGraph(GraphState)

# Add Nodes
# (Fixed typos from the provided snippet here)
workflow.add_node("dispatcher", lambda x: x) # Dummy start node
workflow.add_node("time_agent", time_complexity_agent)
workflow.add_node("space_agent", space_complexity_agent)
workflow.add_node("readability_agent", readability_agent)
workflow.add_node("synthesizer", synthesizer_agent)

# Define flow
workflow.set_entry_point("dispatcher")

# Parallel Execution (Fan-out from dispatcher)
workflow.add_edge("dispatcher", "time_agent")
workflow.add_edge("dispatcher", "space_agent")
workflow.add_edge("dispatcher", "readability_agent")

# Aggregation (Fan-in to synthesizer)
workflow.add_edge("time_agent", "synthesizer")
workflow.add_edge("space_agent", "synthesizer")
workflow.add_edge("readability_agent", "synthesizer")

# End
workflow.add_edge("synthesizer", END)

# Compile graph
app_graph = workflow.compile()

# --- 5. VISUALIZE THE GRAPH ---
if __name__ == "__main__":
    # This block only runs if you execute 'python agent.py' directly.
    # It won't run when imported by app.py or api.py.
    try:
        print("Generating graph image...")
        # Generate PNG data using Mermaid rendering
        png_data = app_graph.get_graph().draw_mermaid_png()
        
        output_filename = "graph_visualization.png"
        with open(output_filename, "wb") as f:
            f.write(png_data)
        print(f"Successfully saved graph image to '{output_filename}'")
    except Exception as e:
        print(f"Could not generate graph image. Error: {e}")
        print("Ensure you have internet access for Mermaid rendering.")