import autogen
import streamlit as st
from autogen import UserProxyAgent, AssistantAgent
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent
from openai.error import RateLimitError

HUMAN_INPUT_MODE = "NEVER"
st.set_page_config(layout="wide")

with st.sidebar:
    model = st.selectbox("GPT Model", ['gpt-4','gpt-3.5'])

    api_key = st.text_input("OpenAI Api Key")
    if model == 'gpt-3.5':
        config_list = [
            {
                'model': 'gpt-3.5-turbo',
                'api_key': api_key,
            },
        ]
    else:
        config_list = [
            {
                'model': 'gpt-4',
                'api_key': api_key,
            },
        ]

    num_agents = st.selectbox("Number of Agents", range(2, 6))
    agents = []
    for i in range(num_agents):
        agents.append(st.expander(f"Agent {i + 1}"))

    agent_objects = []
    available_agents = ['Assistant Agent', 'Product Manager', 'Planner',
                        'Financial Expert', 'Teacher', 'Coder', 'Create Your Own Agent']
    selected_agents = []
    for agent in agents:
        with agent:
            if i == len(agents)-1:
                agent_type = st.radio("Choose Your Agent", ['User Agent'], key=i)
            else:
                agent_type = st.radio("Choose Your Agent", available_agents, key=i, help='''AssistantAgent: An LLM-based agent that can be used to perform tasks such as automated research assistance, chatbots, and more.\n
    UserProxyAgent: A type of agent that can work together with the AssistantAgent on tasks, with the user proxy acting on behalf of the user or asking for approval for certain actions.\n
    Planner: An agent that can suggest coding and reasoning steps for another AI assistant to accomplish a task.\n
    Product Manager: Creative in software product ideas.\n
    Financial Expert: A type of agent that specializes in providing financial advice and managing money for individuals and organizations.\n
    Teacher: A type of agent that simulates a teacher in a learning environment.\n
    Coder: A coder agent is an AI assistant that is designed to help with coding tasks''')
            if agent_type == available_agents[0]:
                agent_objects.append(AssistantAgent("assistant", llm_config={"config_list": config_list}))
                selected_agents.append(agent_type)

            elif agent_type == 'User Agent':
                max_reply = st.selectbox("Max Consecutive Messages",[x for x in range(2,6)], help='It is used to limit the number of consecutive automated replies that the agent can send to another agent during a conversation.')
                agent_objects.append(UserProxyAgent(
                    name="user_proxy",
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    human_input_mode=HUMAN_INPUT_MODE,
                    max_consecutive_auto_reply= max_reply
                ))
                selected_agents.append(agent_type)


            elif agent_type == available_agents[1]:
                agent_objects.append(autogen.AssistantAgent(
                    name="Product_manager",
                    system_message="Creative in software product ideas.",
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    max_consecutive_auto_reply=2,
                    llm_config={"config_list": config_list}
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[2]:
                agent_objects.append(autogen.AssistantAgent(
                    name="planner",
                    llm_config={"config_list": config_list},
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    max_consecutive_auto_reply=2,
                    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."

                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[3]:
                agent_objects.append(autogen.AssistantAgent(
                    name="assistant",
                    llm_config={"config_list": config_list},
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    max_consecutive_auto_reply=2,
                    system_message="You are a financial expert.",
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[4]:
                agent_objects.append(autogen.AssistantAgent(
                    name="assistant",
                    llm_config={"config_list": config_list},
                    max_consecutive_auto_reply=2,
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[5]:
                agent_objects.append(autogen.AssistantAgent(
                    name='coder',
                    llm_config={"config_list": config_list},
                    max_consecutive_auto_reply=2,
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                ))
                selected_agents.append(agent_type)

            elif agent_type == available_agents[6]:
                name = st.text_input('Name', help='The identifier or name assigned to the agent. This might be used to reference or distinguish between multiple agents.')
                system_message= st.text_input('Description', help='An initial message or a descriptor for the agent. It sets the context or role for the agent. It could be an instruction to the agent about its intended behavior.')
                agent_objects.append(autogen.AssistantAgent(
                    name=name,
                    llm_config={"config_list": config_list},
                    max_consecutive_auto_reply=2,
                    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
                    system_message=system_message
                ))
                selected_agents.append(agent_type)
            
        i -= 1

    # chat_initiator = st.selectbox("Chat Initiator", selected_agents)
    agent_init = selected_agents.index('User Agent')

prompt = st.text_input("Prompt")
start = st.button("Start")
if start:
    agent_selected = agent_objects.pop(agent_init)
    try:
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
    except RateLimitError:
        st.error(RateLimitError.user_message)
