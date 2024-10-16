# keyboard layout(s)


msft_prompts = {
    "1": """"
        Who can help Microsoft Partners if they have technical questions 
        and need guidance during the presales or deployment phase of their projects? 
        Use the information found here https://learn.microsoft.com/en-us/partner-center/technical-benefits and list a very brief summary of the services offered. 
        Add the relevant links to the answer.
    """,
    # Multi-step prompt
    "3": ["eerste deel,", "tweede deel,", "derde deel,"],
    # Prompt  Coach
    "7": [
        """
        Hi Copilot, I'd like you to act as my Prompt engineer. Your goal is to help me craft the best possible prompt for my needs. The purpose of the prompt is that I will use it with you, Copilot.
        """,
        """
        You must follow the following process during this chat session: 

        1. Your first response will be to ask me what the prompt should be about. I will provide my answer, but we will need to improve it through continual iterations by going through steps two and three. 
        """,
        """
        2. Based on my input, you will generate two sections. 
            - Revised prompt (Always provide your revised prompt. It should be clear, concise, and easily understood by you) 
            - Use one of the following structures : 
                Structure 1 : Goal, Context, Information, Expectations 
                Structure 2 : Goal, Context, Information sources, Constraints, Example Output
            - Questions (Ask any relevant questions pertaining to what additional information is needed from me for you to improve the prompt). 
        """,
        """
        3. We will continue this iterative process with me providing additional information to you and you continuously updating the prompt in the Revised prompt section so I can use it.
        4. Once we have a final prompt, I will let you know, and we can conclude the chat session. 
""",
    ],
}

prompts = msft_prompts
