from qa_shifter import *
from sensors import *
from hub import *


class process_mst(Procedure): pass
class process_cmd(Procedure): pass

MODE_INT = config.get('LLM', 'MODE')


# SIMULATING EVENTS

# Routines
# turn off the lights in the living room, when the temperature is 25 and the time is 12.00
# set the cooler in the bedroom to 25 degrees and cut the grass in the garden, when the time is 12.00

# Direct Commands
# set the cooler at 27 degrees in the bedroom
# turn off the lights in the living room

# Sensors
s1() >> [simulate_sensor("Be", "Time", "12.00")]
s2() >> [simulate_sensor("Be", "Temperature", "25")]

make_feed() / TEST(X) >> [-TEST(X), reset_ct(), parse_rules(X), parse_deps(), feed_mst(), process_mst(), log_cmd("Feed", X), show_ct(), make_feed()]
make_feed() >> [show_line("\nFeeding KBs ended.\n")]

# Feeding Clauses KB with sentences in FILE_KB_NAME (config.ini)
feed() >> [show_line("\nFeeding KBs from file....\n"), +WAKE("ON"),  +LISTEN("ON"), feed_kbs(), make_feed()]

# Feeding Clauses KB with sentences X
feed(X) >> [show_line("\nFeeding KBs from a sentence....\n"), +WAKE("ON"),  +LISTEN("ON"), +TEST(X), make_feed()]


# Front-End STT

# Start agent command
go() >> [show_line(f"EAD-CogBot started! Bot is running in {MODE_INT} mode..."), +MODE(MODE_INT), Chatbot().start(), set_wait()]


# show higher Clauses kb
hkb() >> [show_fol_kb()]
# show lower Clauses kb
lkb() >> [show_lkb()]

# show lower Clauses kb
expt() >> [export_lkb()]

# initialize Higher Clauses Kb
chkb() >> [log_op(">>> Flushing High Clauses KB..."), clear_hkb()]
# initialize Lower Clauses Kb
clkb() >> [log_op(">>> Flushing Low Clauses KB..."), clear_lkb()]

# chatbot wake word
+message(C, "hello") / WAIT(W) >> [show_line("Starting agent..."), Reply(C, "Hello!"), +WAKE("ON"), +LISTEN("ON"), +CHAT_ID(C), clear_hkb()]
+message(C, "hello") / WAKE("ON") >> [show_line("Restarting agent.."), Reply(C, "Hello again..."), +WAKE("ON"), +LISTEN("ON"), +CHAT_ID(C), clear_hkb()]

# chatbot kbs utilities words
+message(C, "forget") / WAKE("ON") >> [Reply(C, "Okay, short term memory is gone..."), +WAKE("ON"), +CHAT_ID(C), clear_hkb(), reset_ct()]
+message(C, "forget all") / WAKE("ON") >> [Reply(C, "Okay, short and long term memory are gone..."), +WAKE("ON"), +CHAT_ID(C), clear_hkb(), clear_lkb(), reset_ct()]

# handling sentences
+message(C, X) / WAKE("ON") >> [show_line("Handling sentences.."), reset_ct(), +CHAT_ID(C), +MSG(X), manage_msg()]


# LLM (only Query/Answer LLM)
manage_msg() / (MODE("LLM") & MSG(X) & CHAT_ID(C)) >> [show_line("LLM pipeline..."), llm_get(C, X), -MSG(X), log_cmd("LLM", X)]

# AD (Abduction-Deduction with FOL-to_NL response)
manage_msg() / (MODE("AD") & MSG(X) & CHAT_ID(C)) >> [show_line("AD pipeline..."), log_cmd("AD", X), handle_msg()]

# Assertion management (chatbot)
handle_msg() / (MSG(X) & CHAT_ID(C) & check_last_char(X, ".")) >> [Reply(C, "Got it."), -MSG(X), -REASON("ON"), +LISTEN("ON"), parse_rules(X), parse_deps(), feed_mst(), process_mst(), log_cmd("Feed", X), handle_msg()]
# Questions management (chatbot)
handle_msg() / (MSG(X) & CHAT_ID(C) & check_last_char(X, "?")) >> [Reply(C, "Let me think..."), -MSG(X), -LISTEN("ON"), +REASON("ON"), +STT(X), log_cmd("Query", X), qreason(), handle_msg()]
# Otherwise (chatbot)
handle_msg() / (MSG(X) & CHAT_ID(C)) >> [show_line("Direct LLM sentence detected"), -MSG(X), llm_get(C, X), log_cmd("LLM", X), handle_msg()]
# Ending operation (chatbot)
handle_msg() >> [show_ct(), show_line("\n------------- End of operations.\n")]


# Assertion management (shell)
proc(X) / (wfc(X) & check_last_char(X, ".")) >> [show_line("\nGot it."), +WAKE("ON"), -REASON("ON"), +LISTEN("ON"), parse_rules(X), parse_deps(), feed_mst(), process_mst(), log_cmd("Feed", X), show_ct(), -WAKE("ON"), +LISTEN("ON"), show_line("\n------------- End of operations.\n")]
# Questions management (shell)
proc(X) / (wfc(X) & check_last_char(X, "?")) >> [show_line("\nLet me think..."), +MODE("SHELL"), +WAKE("ON"), -LISTEN("ON"), +REASON("ON"), +STT(X), log_cmd("Query", X), qreason(), show_ct(), -WAKE("ON"), show_line("\n------------- End of operations.\n")]
# Domotic command management (shell)
proc(X) / wfc(X) >> [show_line("\nDirect LLM sentence detected"), llm_get_shell(C, X), log_cmd("LLM-shell", X)]
proc(X) >> [show_line("\nError: command not well formed. (for example: proc(\"xxxx\"))\n")]


# Give back X as chatbot answer
+OUT(X) / CHAT_ID(C) >> [Reply(C, X)]

# Turning questions into possible assertions, and reasoning on them until found non-False or completed the generation set (see [QA] in config.ini)
qreason() / (WAKE("ON") & REASON("ON") & ANSWERED('YES') & CAND(Y) & LAST(X)) >> [show_line("\nReasoning successful (other candidates present)."), -CAND(Y), -LAST(X), -ANSWERED('YES'), -REASON("ON"), qreason()]
qreason() / (WAKE("ON") & REASON("ON") & ANSWERED('YES') & LAST(X)) >> [show_line("\nReasoning successful.") , -LAST(X), -ANSWERED('YES'), -REASON("ON"), qreason()]
qreason() / (STT(X) & WAKE("ON") & REASON("ON")) >> [show_line("\nTurning question into fact shapes....\n"), -STT(X), +LAST(X), assert_sequence(X), getcand(), tense_debt_paid(), qreason()]
qreason() / (CAND(X) & WAKE("ON") & REASON("ON")) >> [show_line("\nProcessing candidate....", X), -CAND(X), +GEN_MASK("FULL"), parse_rules(X), parse_deps(), feed_mst(), new_def_clause("ONE", "NOMINAL"), qreason()]

# Conclusion of the evaluation of all candidates
qreason() / (WAKE("ON") & REASON("ON") & MODE("SHELL") & LAST(X)) >> [show_line("\nAll candidates are being unsuccessfully processed."), -REASON("ON"),  qreason()]

# Last hopes of answers from LLM
qreason() / (WAKE("ON") & MODE("SHELL") & LAST(X)) >> [show_line("\nProcessing last hope from LLM (shell): ", X), -MODE("SHELL") , -LAST(X), llm_get_last_shell(C, X)]
qreason() / (WAKE("ON") & MODE("AD") & LAST(X)) >> [show_line("\nProcessing last hope from LLM (chatbot): ", X), -LAST(X), llm_get_last(C, X)]


# qreason() / (WAKE("ON") & REASON("ON") & ANSWERED('YES') & RELATED(X)) >> [-RELATED(X), +OUT(X), qreason()]
# qreason() / (WAKE("ON") & REASON("ON") & ANSWERED('YES')) >> [-ANSWERED('YES')]
# qreason() / (WAKE("ON") & REASON("ON") & RELATED(X)) >> [-RELATED(X), +OUT(X), qreason()]


# Nominal clauses assertion --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
process_mst() / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nGot it.\n"), +GEN_MASK("BASE"), new_def_clause("MORE", "NOMINAL"), process_rule()]
# processing rules --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
process_rule() / IS_RULE("TRUE") >> [show_line("\n------> rule detected!!\n"), -IS_RULE("TRUE"), +GEN_MASK("BASE"), new_def_clause("MORE", "RULE")]

# Generalization assertion
new_def_clause(M, T) / GEN_MASK("BASE") >> [-GEN_MASK("BASE"), preprocess_clause("BASE", M, T), parse(), process_clause(), process_clause_final(), new_def_clause(M, T)]
new_def_clause(M, T) / GEN_MASK(Y) >> [-GEN_MASK(Y), preprocess_clause(Y, M, T), parse(), process_clause(), process_clause_final(), new_def_clause(M, T)]
new_def_clause(M, T) / CHAT_ID(C) >> [show_line("\n------------- Done.\n")]


# IoT Reasoning
process_cmd() / (WAKE("ON")) >> [show_line("\nProcessing IoT command...\n"), assert_command(), parse_command(), parse_routine()]

