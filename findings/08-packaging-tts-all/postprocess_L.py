# postprocess.py - text fixes applied to every hypothesis before it is written.
#
# DELIBERATELY ALMOST EMPTY IN PHASE 1. The orthographic rules belong to
# notebook 07, and each one has to earn its place with a paired bootstrap on the
# official dev set before it goes in here. A rule that "looks obviously right"
# is how a submission quietly gets worse: the E4 error table shows the reference
# disagreeing with itself in both directions (gak->nggak 62 times, nggak->gak 33
# times), so a blanket rewrite fixes one column and breaks the other.
#
# What IS safe now is whitespace: it cannot change a token, only how tokens are
# separated, and the official scorer collapses runs of spaces anyway.
#
# Notebook 07 fills RULES below. Keep every entry measurable in isolation.
RULES = []


def postprocess(text):
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    for pattern, replacement in RULES:
        text = pattern.sub(replacement, text)
    return " ".join(text.split()).strip()
