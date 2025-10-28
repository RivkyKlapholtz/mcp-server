import requests
from typing import List
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain.chat_models import ChatOpenAI

MCP_SERVER_URL = "http://localhost:8000"

def fetch_tools_from_mcp() -> List[ToolNode]:
    resp = requests.get(f"{MCP_SERVER_URL}/tools")
    resp.raise_for_status()
    tools_json = resp.json()
    tools: List[ToolNode] = []

    for tool_def in tools_json:
        name = tool_def["name"]
        description = tool_def["description"]

        def make_func(n):
            def func_wrapper(**kwargs):
                call_resp = requests.post(
                    f"{MCP_SERVER_URL}/call",
                    json={"name": n, "arguments": kwargs}
                )
                call_resp.raise_for_status()
                return call_resp.json().get("result", call_resp.json().get("error"))
            return func_wrapper

        tools.append(ToolNode(name=name, func=make_func(name), description=description))

    return tools

def main():
    # 1. Fetch tools
    tools = fetch_tools_from_mcp()

    # 2. Setup LLM
    llm = ChatOpenAI(temperature=0)

    # 3. Create a prompt template
    prompt_template = "Tell me a {adjective} joke"
    prompt = PromptTemplate(input_variables=["adjective"], template=prompt_template)

    # 4. Build a LangGraph agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
    )

    # 5. Run a prompt
    user_prompt = input("Enter your request: ")
    result = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
    print("Agent result:", result)

if __name__ == "__main__":
    main()
