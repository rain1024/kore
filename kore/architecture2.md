architecture
    group agent_system(cloud)[AI Agent System]

    service user(server)[User] in agent_system
    service agent(server)[Agent] in agent_system
    service llm(database)[LLM] in agent_system
    service memory(disk)[Memory] in agent_system
    service tools(disk)[Tools] in agent_system
    service knowledge(database)[Knowledge] in agent_system

    user:R -- L:agent
    agent:R -- L:llm
    agent:B -- T:memory
    agent:B -- T:tools
    llm:B -- T:knowledge
