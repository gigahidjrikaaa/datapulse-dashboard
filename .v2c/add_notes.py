# -*- coding: utf-8 -*-
"""Write presenter notes into board_deck.pptx and export a rehearsal script.

Language rules for the notes (for a non-native speaker):
- short sentences, one idea each
- everyday words (no "forfeit", "lapse", "stagnation", "EBITDA")
- every number stays exactly as it appears on the slide
- SAY = the words to speak; everything else is help for the presenter only
"""
import re
import shutil

from pptx import Presentation

SRC = "presentation/board_deck.pptx"
BACKUP = ".v2c/board_deck_backup_pre_notes_v2.pptx"
MD = "presentation/board_deck_presenter_notes.md"

NOTES = [
    # 1 Title (0:30)
    ("0:30", """SAY: "Good morning. We studied four years of sales data - 51,290 order lines. We found one thing: Global Superstore does not have a growth problem. It has a pricing problem. In the next ten minutes we will show you where the profit is going, and a three-step plan that brings back $1.23M without spending any new money."
DELIVERY: Say one line about the team - Syndicate 6, seven analysts - then move on. Do not read the name list.
TRANSITION: "Let us start with the headline.\""""),
    # 2 Executive summary (0:45)
    ("0:45", """SAY: Four numbers tell the whole story. Revenue almost doubled, from $2.26M to $4.30M - up 90.3% - so the rumours about falling sales are wrong. But margin stayed at 11.6%. Why? One in four order lines was sold at a loss, and those losses destroyed $920,646. The fix is not more sales - it is three actions that bring back $1.23M, an 84% increase, with no new money.
DELIVERY: Point at each of the four cards as you say it. Pause after "$920,646".
IF ASKED "is $1.23M realistic?": "It is the base case of our simulator. Even the careful case gives +$0.91M - slide 14 shows that test."
TRANSITION: "First: is the growth real?\""""),
    # 3 Growth (0:30)
    ("0:30", """SAY: The growth is real, and it comes from more orders. Revenue rose every year: +18.5%, +27.2%, +26.3%. Operating profit more than doubled, to $504K. Orders grew from 4,440 to 8,531. The average order stayed at about $505. We grew by adding customers, not by raising prices - and that is why margin never improved.
TRANSITION: "Look at the margin line: every extra dollar came with the same thin profit.\""""),
    # 4 Margin (0:30)
    ("0:30", """SAY: Margin stayed between 11.0% and 11.9% for four years. Profit grew at the same speed as sales, so getting bigger did not make us more profitable. Why? The company pays bonuses for sales volume, so nobody protected the price. From today, margin - not revenue - is the number to watch.
TRANSITION: "So where does the profit go? One in four orders loses money.\""""),
    # 5 Profit leakage (0:45)
    ("0:45", """SAY: Read the bridge from left to right. Orders that make money bring in $2.39M - that part is strong. But 12,544 order lines - one in four - were sold below cost, and they destroyed $920,646 of it. What is left: $1.47M.
DELIVERY: Slow down on "one in four".
IF ASKED "is 24.5% normal?": "Healthy shops lose money on only a few percent of orders. Our number is high because of our own pricing rules - slide 8 shows exactly how."
TRANSITION: "Where is the loss? First, the map.\""""),
    # 6 Geography (0:30)
    ("0:30", """SAY: 29 of 147 countries lose money. Turkey (-$98K) and Nigeria (-$81K) are the biggest. Both sold with 60-70% discounts, and we paid their shipping costs ourselves. This is a policy problem, not a market problem: EMEA earns 5.4% margin while our healthy markets earn 12-13%.
TRANSITION: "One product tells the same story.\""""),
    # 7 Tables (0:30)
    ("0:30", """SAY: 16 of 17 product lines make money - Copiers +$259K, Phones +$217K. Only Tables loses: -$64K on $757K of sales, with a 29.1% average discount and the highest shipping cost per item. That is why Furniture earns 6.9% and Technology 14.0%.
TRANSITION: "But the biggest single cause is one number: 20%.\""""),
    # 8 Discount cliff (1:00)
    ("1:00", """SAY: This is the most important chart in the deck. Below 20% discount, every group makes money: +25.3% with no discount, still +9.9% at 10-20%. Above 20%, every group loses: -5.5%, then -111% past 50%. 11,328 order lines - 22.1% - crossed that line and lost $814,682. That is 88.5% of all the money we lose.
DELIVERY: Move your hand along the fall. Pause on "88.5%".
NEW ON THIS SLIDE: past 50% off, 100% of orders lose money. The correlation between discount and profit is -0.60 (rank) - proof that the damage is a cliff, not a slow slide.
IF ASKED "why exactly 20%?": "Because that is where the data turns negative. It is not a round number we picked - our margin cannot survive discounts deeper than 20%."
TRANSITION: "Shipping is the second cause.\""""),
    # 9 Freight (0:30)
    ("0:30", """SAY: Critical-priority orders spend 23.8% of their sales value on shipping; Same Day spends 17.4%. Standard Class spends only 8.1%. Across the company, shipping is 10.7% of sales, and we never charge it to the customer. Big discounts and heavy shipping land on the same orders.
TRANSITION: "Put the three causes together and the picture is simple.\""""),
    # 10 Root causes (0:30)
    ("0:30", """SAY: Three root causes, and all three are our own rules. Uncontrolled discounts: +$1.03M to fix. Direct shipping to Turkey and Nigeria: +$0.18M. Free freight on Tables: +$0.05M. The recovery is bigger than the $921K leak, because capping discounts turns those orders back into profitable ones.
TRANSITION: "Before the plan - what else did we consider?\""""),
    # 11 Alternatives (0:45)
    ("0:45", """SAY: We tested three other ideas, and rejected all three. First: raise prices but allow bigger discounts. No - the loss follows the size of the discount, not the list price: 88.5% of the lost money sits above 20%. Second: stop selling in Turkey and Nigeria. No - that gives up $163K of sales; local partners remove the same $179K loss and keep every sale. Third: ask all carriers for cheaper shipping. Not enough - a 10% better price returns about $0.14M after a year of talks, and does not touch the $814,682 discount problem.
IF ASKED "why not raise prices anyway?": "Higher prices hit the 75.5% of orders that are healthy. The cap only touches the 22% that lose money."
TRANSITION: "So here is the plan.\""""),
    # 12 Plan (0:45)
    ("0:45", """SAY: Three actions, each with an owner and a date. One: cap all discounts at 20% in the ordering system - Chief Commercial Officer, months 1-2, +$1.03M. Two: move Turkey and Nigeria to local delivery partners - VP Supply Chain, months 3-4, +$0.18M. Three: charge shipping costs on Tables - Head of Merchandising, months 5-7, +$0.05M. Each action has a KPI, shown on the slide.
TRANSITION: "After customer losses, here is the money.\""""),
    # 13 Financial impact (0:30)
    ("0:30", """SAY: From $1.47M today: add $1.03M from the cap, $0.18M from local partners, $0.05M from freight fees, take away $0.02M for customers who leave - and we reach $2.70M. Margin goes from 11.6% to 19.9%. That is about $0.31M more per year.
IF ASKED about the 5%: "It is a safety margin for customers who leave. The next slide shows we are safe even at 7%."
TRANSITION: "And the plan survives a stress test.\""""),
    # 14 Sensitivity (0:15)
    ("0:15", """SAY: The careful case - a 25% cap, no fees, 7% customer loss, half the local-partner change - still adds +$0.91M, to $2.37M. The strong case reaches $3.0M. One sentence: the recommendation does not depend on optimism.
TRANSITION: "Execution is a four-phase plan over twelve months.\""""),
    # 15 Roadmap (0:30)
    ("0:30", """SAY: Phase 1, months 1-2, is one rule in the ordering system - no new money, no new software. Phase 2, months 3-4, cuts the regional loss by 70%. Phase 3, months 5-7, brings Tables back to zero loss. Phase 4, months 8-12, makes it permanent with quarterly reviews and a margin committee. Target: margin above 15.5%.
TRANSITION: "So what does the future look like if we do this?\""""),
    # 16 What happens next (0:30)
    ("0:30", """SAY: Three predictions, all tested on data the models never saw. One: FY2015 revenue will be about $5.28M, up 23%, if trends continue. Two: the 20% cap keeps almost all volume - about 101% - because big discounts never brought many sales. Three: we can name the customers most likely to stop buying. The riskiest tenth of them leave at almost three times the average rate.
DELIVERY: Say slowly: "the cap costs us almost no volume." This is the key new fact.
IF ASKED "how reliable are these numbers?": "The forecast was tested on FY2014: error 10%. The churn model was tested on held-out customers: 0.80 AUC."
TRANSITION: "That brings us to the three approvals we need today.\""""),
    # 17 Board decision (0:30)
    ("0:30", """SAY: Three decisions. Approve the 20% discount cap - manager approval between 15% and 20%, blocked above 20%. Approve the change to local delivery partners in Turkey and Nigeria. Start a margin committee led by the CFO. No new money is needed; first savings come inside 90 days; the full gain is $1.23M and a 19.9% margin.
IF ASKED "what if we approve only the cap?": "The cap alone gives $1.03M of the $1.23M - but Turkey and Nigeria keep losing $179K, so we would ask for that step again within a year."
TRANSITION: "Thank you - we are ready for your questions.\""""),
    # 18 Close (0:15)
    ("0:15", """SAY: End with the quote, then: "This company is losing $921K a year. We know exactly where the money goes, and the repair is three decisions - not a rescue plan. We ask for approval this quarter."
Q&A PREP - the three hardest questions:
1. "Is 5% customer loss too optimistic?" - The careful case uses 7% and still gains +$0.91M (slide 14).
2. "Why not simply raise prices?" - The loss follows the discount size, not the list price; 88.5% of losses sit above the 20% cap (slide 11).
3. "Is the local-partner change risky?" - It goes step by step, per country, with a break-even target in 90 days (slide 12)."""),
]

SECONDS = [int(m.split(":")[0]) * 60 + int(m.split(":")[1]) for m, _ in NOTES]
TOTAL_MIN = sum(SECONDS) / 60.0

shutil.copyfile(SRC, BACKUP)

p = Presentation(SRC)
assert len(p.slides) == len(NOTES), f"{len(p.slides)} slides vs {len(NOTES)} notes"
for i, (slide, (clock, body)) in enumerate(zip(p.slides, NOTES), 1):
    header = f"[{clock} - Slide {i} of {len(NOTES)}]"
    slide.notes_slide.notes_text_frame.text = header + "\n" + body
p.save(SRC)


def fmt_line(line: str) -> str:
    """Bold the directive label at the start of a line (SAY, DELIVERY, ...)."""
    stripped = line.strip()
    if not stripped:
        return ""
    m = re.match(r"^(SAY|DELIVERY|TRANSITION|Q&A PREP[^:]*|IF ASKED[^:]*):(.*)$", stripped)
    if m:
        return f"**{m.group(1)}:**{m.group(2)}"
    return stripped


LABEL = re.compile(r"^(SAY|DELIVERY|TRANSITION|Q&A PREP|IF ASKED)")
lines = [
    "# Presenter Notes - Global Superstore: The Revival Strategy",
    "",
    "18 slides. Target: 10 minutes of speaking + 5 minutes of questions.",
    f"Total speaking time in these notes: {TOTAL_MIN:.1f} minutes.",
    "",
    "**How to use this file:** read only the **SAY** lines out loud - they are written in "
    "words you can say directly. **DELIVERY**, **IF ASKED** and **TRANSITION** lines are "
    "help for you, not for the audience. If you lose your place: say the **SAY** line of "
    "the current slide, then move to the next slide.",
    "",
]
for i, (clock, body) in enumerate(NOTES, 1):
    lines.append(f"## Slide {i} - {clock}")
    lines.append("")
    for raw in body.split("\n"):
        out = fmt_line(raw)
        is_label = bool(LABEL.match(raw.strip()))
        is_list = bool(re.match(r"^\d+\.", raw.strip()))
        if is_label and lines[-1] != "":
            lines.append("")
        lines.append(out)
        if not is_label and not is_list and out != "":
            lines.append("")
    lines.append("")

with open(MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"notes written to {len(NOTES)} slides; total {TOTAL_MIN:.1f} min; script -> {MD}; backup -> {BACKUP}")
