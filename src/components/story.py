"""The storyline that stitches the dashboard into a single Board narrative.

Senior-analyst presentation pattern (pyramid principle):
- the answer comes first, at the top of every chapter, not at the bottom;
- each chapter is titled with its finding (an action title), never with a topic label;
- every chapter answers the exact question the previous chapter raises, and hands off
  to the next one explicitly.
"""

import streamlit as st

STORY_CHAPTERS = [
    {"key": "answer", "label": "The Answer First", "question": "What is the one thing the Board must know?"},
    {"key": "ch1", "label": "Ch. 1 - The Verdict", "question": "Is Global Superstore really underperforming?"},
    {"key": "ch2", "label": "Ch. 2 - Where It Leaks", "question": "Where exactly is the money leaking?"},
    {"key": "ch3", "label": "Ch. 3 - Why It Happens", "question": "Why does it happen?"},
    {"key": "ch4", "label": "Ch. 4 - The Fix", "question": "What should the company do in the next 6-12 months?"},
    {"key": "ch5", "label": "Ch. 5 - What's Next", "question": "What happens after the fix lands?"},
    {"key": "appendix", "label": "Appendix", "question": "Can every number be verified line by line?"},
]


def render_story_ribbon(current_key: str, answer: str, next_line: str | None = None) -> None:
    """Render the story ribbon at the top of a chapter: position, question, answer, hand-off.

    Args:
        current_key: This chapter's key in STORY_CHAPTERS.
        answer: The chapter's answer, stated up front (pyramid principle).
        next_line: One-line hand-off to the next chapter.
    """
    order = {c["key"]: i for i, c in enumerate(STORY_CHAPTERS)}
    cur = order[current_key]
    chips = []
    for i, ch in enumerate(STORY_CHAPTERS):
        if i < cur:
            chips.append(f"✓ {ch['label']}")
        elif i == cur:
            chips.append(f"**{ch['label']}**")
        else:
            chips.append(ch["label"])
    st.caption("  →  ".join(chips))
    st.markdown(f"**This chapter answers:** {STORY_CHAPTERS[cur]['question']}  \n**The answer, up front:** {answer}")
    if next_line:
        st.caption(f"Up next → {next_line}")
