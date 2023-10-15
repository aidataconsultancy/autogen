import autogen
import openai
import streamlit as st
from autogen import config_list_from_json, UserProxyAgent, AssistantAgent
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent

HUMAN_INPUT_MODE = "NEVER"
st.set_page_config(layout="wide")

with st.sidebar:

    api_key = st.text_input("OpenAI Api Key")
    openai.api_key = api_key
    filter_dict = {
        "api_type": ["open_ai"],
        "model": ["gpt-3.5-turbo"],
    }
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": {
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-35-turbo-v0301",
            },
        },
    )

    # config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST", filter_dict=filter_dict)

    num_agents = st.selectbox("Number of Agents", range(2, 6))
    agents = []
    for i in range(num_agents):
        agents.append(st.expander(f"Agent {i + 1}"))

    agent_objects = []
    available_agents = ['Assistant Agent', 'UserProxy Agent', 'MathUserProxy Agent', 'Product Manager', 'Planner',
                        'Financial Expert', 'Teacher']
    selected_agents = []
    for agent in agents:
        with agent:
            agent_type = st.radio("Choose Your Agent", available_agents, key=i)
            if agent_type == available_agents[0]:
                agent_objects.append(AssistantAgent("assistant", llm_config={"config_list": config_list}))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[1]:
                agent_objects.append(UserProxyAgent(
                    name="user_proxy",
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    code_execution_config=False,
                    human_input_mode="NEVER"
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[2]:
                agent_objects.append(MathUserProxyAgent(
                    name="mathproxyagent",
                    human_input_mode="NEVER",
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[3]:
                agent_objects.append(autogen.AssistantAgent(
                    name="Product_manager",
                    system_message="Creative in software product ideas.",
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    llm_config={"config_list": config_list}
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[4]:
                agent_objects.append(autogen.AssistantAgent(
                    name="planner",
                    llm_config={"config_list": config_list},
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."

                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[5]:
                agent_objects.append(autogen.AssistantAgent(
                    name="assistant",
                    llm_config={"config_list": config_list},
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    system_message="You are a financial expert.",
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[6]:
                agent_objects.append(autogen.AssistantAgent(
                    name="assistant",
                    llm_config={"config_list": config_list},
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                ))
                selected_agents.append(agent_type)

        i -= 1

    chat_initiator = st.selectbox("Chat Initiator", selected_agents)
    agent_init = selected_agents.index(chat_initiator)

prompt = st.text_input("Prompt")
start = st.button("Start")
if start:
    agent_selected = agent_objects.pop(agent_init)
    if len(agent_objects) > 1:
        groupchat = autogen.GroupChat(agents=agent_objects, messages=[], max_round=12)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})
        agent_selected.initiate_chat(manager, message=prompt, silent=True)
        for messages in agent_selected.chat_messages:
            for message in messages.chat_messages[agent_objects[0]]:
                with st.chat_message(message['role']):
                    st.markdown(message['content'])
    else:
        agent_selected.initiate_chat(agent_objects[0], message=prompt, silent=True)
        for message in agent_objects[0].chat_messages[agent_selected]:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
