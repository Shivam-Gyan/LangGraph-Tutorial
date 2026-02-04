from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from states import PostState, EvaluationSchema


def generation_prompt(state:PostState):
    
    # prompt for generating a viral tweet
    messages = [
        SystemMessage(
            content=(
                "You are a witty, clever, and highly creative social media influencer "
                "known for writing short viral tweets with sharp humor, relatable observations, "
                "and strong punchlines."
            )
        ),
        HumanMessage(
            content=f"""
    Write ONE short, original, and hilarious tweet about: "{state.title}".

    Strict rules:
    - Maximum 280 characters.
    - Do NOT use question–answer format.
    - Do NOT include hashtags unless absolutely necessary for humor.
    - No emojis unless they improve the punchline.
    - Must feel natural, human, and meme-ready.
    - Use simple everyday English.
    - Prefer observational humor, irony, sarcasm, or cultural references.
    - End with a strong punchline or twist.
    - Avoid clichés, generic motivation, or AI-sounding phrases.

    Output format:
    Return ONLY the final tweet text.
    Do not add explanations, quotes, or extra lines.
    """
        )
    ]
    return messages


def evaluation_prompt(state:PostState):

    # prompt for evaluation based on specific criteria
    messages = [
        SystemMessage(
            content=(
                "You are a strict and discerning social media critic with a sharp eye for humor, originality, and viral potential. "
                "Your job is to evaluate the quality of a tweet based on specific criteria and provide constructive feedback."
            )
        ),
        HumanMessage(
            content=f"""
    Evaluate the following tweet based on these criteria:

    1. Humor: Is the tweet genuinely funny? Does it use clever wordplay, irony, sarcasm, or relatable observations?
    2. Originality: Is the tweet unique and creative? Does it avoid clichés and generic phrases?
    3. Viral Potential: Does the tweet have elements that could make it go viral, such as a strong punchline, cultural references, or meme-worthy content?

    Tweet to evaluate:
    "{state.post}"

    Provide your evaluation in the following format:

    Evaluation:
    - Humor: (score out of 10) + brief explanation
    - Originality: (score out of 10) + brief explanation
    - Viral Potential: (score out of 10) + brief explanation

    Feedback:
    Provide specific feedback on how to improve the tweet in terms of humor, originality, and viral potential. Be constructive and actionable.
    """
        )
    ]
    return messages


def optimise_prompt(state:PostState):

    # prompt for optimisation based on feedback
    messages = [
        SystemMessage(
            content=(
                "You are an elite viral tweet editor and comedy punch-up specialist. "
                "Your job is to transform weak or rejected tweets into highly shareable, "
                "original, and genuinely funny viral tweets using the provided feedback. "
                "You rewrite with precision, stronger punchlines, tighter wording, and "
                "better relatability—never generic or AI-sounding."
            )
        ),
        HumanMessage(
            content=f"""
    Your task is to REWRITE and IMPROVE a rejected tweet so that it would PASS a strict viral-quality evaluation.

    ### Topic
    "{state.title}"

    ### Original Tweet
    {state.post}

    ### Feedback from critic
    "{state.feedback}"

    ---

    ### Rewrite requirements (MANDATORY)

    You must:
    - Fix **every issue mentioned in the feedback**
    - Make the tweet **more original, funny, punchy, and relatable**
    - Deliver a **clear punchline or twist ending**
    - Keep it **natural, human, and meme-ready**
    - Stay **under 280 characters**
    - Use **simple everyday English**
    - Preserve relevance to the **topic**

    You must NOT:
    - Use **question–answer joke format**
    - Write a **traditional setup–punchline joke**
    - Sound **generic, motivational, or AI-generated**
    - Add explanations, hashtags, or emojis unless essential for humor
    - Repeat the original tweet wording unless significantly improved

    ---

    ### Quality bar for approval

    The rewritten tweet should feel like:
    - Something that could **realistically go viral**
    - Worth **liking, sharing, or reposting**
    - **Sharper and funnier** than the original in a noticeable way

    If the improvement is minor, **rewrite again internally** until it is clearly stronger.

    ---

    ### Output rules (STRICT)

    Return **ONLY the final rewritten tweet text**.

    Do NOT include:
    - Quotes
    - Explanations
    - Multiple options
    - Extra lines
    - Any text outside the single final tweet
    """
        )
    ]
    return messages