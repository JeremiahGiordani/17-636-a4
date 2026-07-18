# Reflection

The most striking lesson was how completely the *quality of the loop's stop
condition* determined whether the loop was useful or dangerous. The lecture
warned that a loop with a fuzzy goal becomes a "confident token furnace" that
optimizes toward a vague sentence, and I felt exactly why. By spending the plan
stage writing the acceptance tests *before* any implementation, the vague goal
"build a spreadsheet" became a precise, machine-checkable target — 55 concrete
cases like `=1+2*3 → 7` and `circular reference → error`. That one decision
changed everything downstream: the build agent had an unambiguous definition of
done, the loop could verify completion without me reading every line, and I
could trust the result because a `git diff` proved the test files were unchanged
between the plan and build commits — so the agent had to make the *code* correct
rather than weaken the *tests*. In other words, the hard and valuable
engineering work moved from writing code to specifying "done" well; the loop
just executed against it. Loop engineering didn't remove the need for judgment,
it relocated it to the front — into designing a goal precise enough to safely
automate against.
