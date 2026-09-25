# -*- coding: utf-8 -*-
"""Write presenter notes into board_deck.pptx and export a rehearsal script."""
import copy
from pptx import Presentation

SRC = "presentation/board_deck.pptx"
BACKUP = ".v2c/board_deck_backup_pre_notes_v2.pptx"
MD = "presentation/board_deck_presenter_notes.md"

NOTES = [
    # 1 Title (0:30)
    ("0:30", """SAY: "Good morning. Four years of transaction data - 51,290 order lines - and one finding: Global Superstore does not have a growth problem. It has a pricing problem. In the next ten minutes we will show you exactly where the profit leaks, and a three-lever plan that recovers $1.23M without a dollar of new capital."
DELIVERY: One line of team intro - Syndicate 6, seven analysts - then move. Do not read the roster aloud.
TRANSITION: "Let us start with the headline number.\""""),
    # 2 Executive summary (0:45)
    ("0:45", """SAY: Four numbers tell the whole story. Revenue nearly doubled, $2.26M to $4.30M, up 90.3% - so the rumors of stagnation are false. Yet margin is stuck at 11.6%. Why? One in four order lines sells at a loss, destroying $920,646. The fix is not more sales - it is three policy levers that recover $1.23M, an 84% uplift, with zero new capital.
DELIVERY: Point at each of the four cards as you name it. Pause after "$920,646".
IF ASKED "is $1.23M realistic?": It is the base case of our simulator; even the conservative case returns +$0.91M - slide 14 covers the stress test.
TRANSITION: "First, the diagnosis. Is the growth real?\""""),
    # 3 Growth (0:30)
    ("0:30", """SAY: Growth is genuine and volume-driven. Revenue rose every single year - +18.5%, +27.2%, +26.3% - and operating profit more than doubled to $504K. Orders grew from 4,440 to 8,531; average order value stayed flat at about $505. We grew by adding customers and orders, not by raising prices - which is precisely why margin never improved.
TRANSITION: "Zoom out and the pattern is stark: every extra dollar arrived at the same thin margin.\""""),
    # 4 Margin (0:30)
    ("0:30", """SAY: Margin hovered between 11.0% and 11.9% for four straight years - profit grew exactly in line with revenue, so scale bought us nothing. The reason is incentive design: we measure and pay for gross volume, so nobody defended price. Margin - not revenue - is the number this Board should track from here.
TRANSITION: "So where does the profit actually go? A quarter of everything we sell loses money.\""""),
    # 5 Profit leakage (0:45)
    ("0:45", """SAY: Walk the bridge. Profitable lines earn $2.39M - that core is strong on its own. But 12,544 lines - one in four - were priced below cost and wiped out $920,646 of it. Reported profit: $1.47M. Our healthy core is being taxed by our own pricing.
DELIVERY: Slow down on "one in four".
IF ASKED "is 24.5% normal?": Healthy retail runs low-single-digit loss-line rates. Ours is an outlier caused by policy, not by the market - slide 8 shows the exact mechanism.
TRANSITION: "Where is the loss concentrated? First, geography.\""""),
    # 6 Geography (0:30)
    ("0:30", """SAY: 29 of 147 countries are net-negative, and Turkey (-$98K) and Nigeria (-$81K) carry most of the deficit. Both were sold at 60-70% average discounts, with cross-border freight absorbed centrally. This is a company-policy loss, not a market loss: EMEA runs 5.4% margin against 12-13% in our healthy markets.
TRANSITION: "One product line tells exactly the same story.\""""),
    # 7 Tables (0:30)
    ("0:30", """SAY: Sixteen of seventeen sub-categories are profitable - Copiers +$259K, Phones +$217K. Tables is the only loser: -$64.1K on $757K of sales, carrying a 29.1% average discount plus the highest freight per unit in the catalogue. That drags Furniture to a 6.9% margin against Technology's 14.0%.
TRANSITION: "But the biggest single cause is a line you can draw on a chart: twenty percent.\""""),
    # 8 Discounting (1:00)
    ("1:00", """SAY: This is the most important chart in the deck. Below 20% discount, every band is profitable: +25.3% with no discount, still +9.9% at 10-20%. Above 20%, every band loses: -5.5%, worsening to -111% past 50%. 11,328 lines - 22.1% of the ledger - were priced past that line and lost $814,682: that is 88.5% of ALL loss dollars.
DELIVERY: Trace the cliff with your hand. Pause at "88.5%".
IF ASKED "why 20% exactly?": It is where the data inverts, not a round number we picked - gross margin cannot carry concessions deeper than 20%.
TRANSITION: "Discounting has an accomplice: freight.\""""),
    # 9 Freight (0:30)
    ("0:30", """SAY: Critical-priority orders spend 23.8% of their sales value on freight; Same Day spends 17.4% - against 8.1% for Standard Class, a third of the rate. Company-wide, freight is 10.7% of sales and is never charged back. Deep discounts and heavy freight land on the same orders - that is why they never recover.
TRANSITION: "Put the three together and the root causes are simple and few.\""""),
    # 10 Root causes (0:30)
    ("0:30", """SAY: Three root causes, all policy, none market-driven. Uncontrolled discounting, worth +$1.03M to fix. Loss-making overseas territories served direct, +$0.18M. Bulky Tables freight never billed, +$0.05M. Recovery exceeds the reported $921K leak because capping discounts returns those lines to positive margin - not just to break-even.
TRANSITION: "Before we commit to this plan - what else did we consider?\""""),
    # 11 Alternatives (0:45)
    ("0:45", """SAY: Three alternatives, three eliminations. First: raise list prices and allow deeper discounts - rejected, because the leak follows the discount depth, not the list price: 88.5% of loss dollars sit above the 20% line, so a bigger cap re-opens the wound. Second: exit Turkey and Nigeria - rejected: it forfeits $163K of revenue; 3PL removes the same $179K loss while keeping every sale. Third: renegotiate all carrier rates - demoted to support: a realistic 10% cut returns about $0.14M after a year of contracting and never touches the $814,682 discount leak.
IF ASKED "why not raise prices anyway?": A price rise hits our 75.5% healthy lines too. The cap only touches the 22% that lose money.
TRANSITION: "That leaves the three-lever plan - here it is.\""""),
    # 12 Plan (0:45)
    ("0:45", """SAY: Three initiatives, each with an owner and a date. One: pricing governance - a hard 20% cap in order entry - Chief Commercial Officer, months 1-2, +$1.03M. Two: Turkey and Nigeria restructured to bonded third-party logistics - VP Global Supply Chain, months 3-4, +$0.18M. Three: Tables freight pass-through and repricing - Head of Merchandising, months 5-7, +$0.05M. Note the KPI column: the first one is "no order above 15% discount below 2% of orders".
TRANSITION: "Net of churn, here is the money.\""""),
    # 13 Financial impact (0:30)
    ("0:30", """SAY: From $1.47M baseline: plus $1.03M from the cap, plus $0.18M from 3PL, plus $0.05M freight, minus $0.02M for a 5% churn allowance - landing at $2.70M projected. Margin moves from 11.6% to 19.9%. That is about $0.31M a year on the same run-rate.
IF ASKED about the 5% churn: It is a deliberate penalty for price-sensitive buyers who walk. The stress test on the next slide shows we are robust even at 7%.
TRANSITION: "And the plan holds under stress.\""""),
    # 14 Sensitivity (0:15)
    ("0:15", """SAY: The conservative case - a 25% cap, no surcharge, 7% churn, half the 3PL transition - still lifts profit +$0.91M to $2.37M. The aggressive case reaches $3.0M. One sentence: the recommendation does not depend on optimism.
TRANSITION: "Execution is a four-phase, twelve-month program.\""""),
    # 15 Roadmap (0:30)
    ("0:30", """SAY: Phase 1, months 1-2, is an order-entry rule - no capital, no new systems. Phase 2, months 3-4, cuts the regional loss by 70%. Phase 3, months 5-7, brings Tables back to break-even. Phase 4, months 8-12, makes it permanent: quarterly margin audits and a standing margin committee, with company margin above 15.5% as the exit target.
TRANSITION: "So what does the future look like if we execute?\""""),
    # 16 What happens next (0:30)
    ("0:30", """SAY: Before the decision - what happens next. Three answers, all model-based and all tested on data the models never saw. One: if trends hold, FY2015 revenue lands at $5.3M, +23%. Two: capping discounts at 20% keeps essentially all volume - measured from our own ledger, not assumed. Three: the riskiest tenth of our customers lapse at nearly three times the average rate, and we can name them.
DELIVERY: "Volume-neutral" is the phrase to land - the cap costs almost no demand.
IF ASKED "how reliable are these numbers?": the forecast's error on unseen data was 10%; the churn model separates leavers from stayers at 0.80 AUC.
TRANSITION: "Which brings us to the three approvals we need today.\""""),
    # 16 Board decision (0:30)
    ("0:30", """SAY: Three decisions. Approve the 20% discount cap with VP sign-off between 15% and 20% and a hard block above 20%. Authorize the 3PL transition for Turkey and Nigeria. Charter a margin committee chaired by the CFO. Zero new capital; first savings inside 90 days; +$1.23M and a 19.9% margin on the full ledger.
IF ASKED "what if we only approve the cap?": The cap alone delivers $1.03M of the $1.23M - but the territories keep bleeding $179K, so we would be back asking for phase 2 within the year.
TRANSITION: "Thank you - we are ready for your questions.\""""),
    # 17 Close (0:15 + Q&A)
    ("0:15", """SAY: Close on the quote, then: "The ship is taking on $921K a year. We know exactly where the leak is, and the repair is three decisions - not a rescue plan. We recommend approval this quarter."
Q&A PREP - the three toughest questions:
1. "Is 5% churn not optimistic?" - Conservative case carries 7% churn and still returns +$0.91M (slide 14).
2. "Why not simply raise prices?" - The leak follows discount depth, not list price; 88.5% of losses sit above the 20% cap (slide 11).
3. "3PL execution risk in volatile markets?" - Phased and reversible per country, bonded master distributors, break-even KPI inside 90 days (slide 12)."""),
]

SECONDS = [int(m.split(":")[0]) * 60 + int(m.split(":")[1]) for m, _ in NOTES]
TOTAL_MIN = sum(SECONDS) / 60.0

import shutil
shutil.copyfile(SRC, BACKUP)

prs = Presentation(SRC)
assert len(prs.slides) == len(NOTES), f"{len(prs.slides)} slides vs {len(NOTES)} notes"
for i, (slide, (clock, body)) in enumerate(zip(prs.slides, NOTES), 1):
    header = f"[{clock} - Slide {i} of {len(NOTES)}]"
    slide.notes_slide.notes_text_frame.text = header + "\n" + body
prs.save(SRC)

lines = ["# Board Deck - Presenter Notes",
         "",
         "Global Superstore · Revival Strategy - 10-minute briefing + 5-minute Q&A.",
         f"Total: {TOTAL_MIN:.1f} minutes across {len(NOTES)} slides.", ""]
for i, (clock, body) in enumerate(NOTES, 1):
    lines.append(f"## Slide {i} - {clock}")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
with open(MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"notes written to {len(NOTES)} slides; total {TOTAL_MIN:.1f} min; script -> {MD}; backup -> {BACKUP}")
