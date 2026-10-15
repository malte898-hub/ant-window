# The Ant That Changed Its Mind for AI agent swarms

Oct 15, 2026 · Malte Barth

### Headless swarms of AI agents get stuck. Ants show the fix: forget, and take a few random turns.

**A small AI research project rebuilt a classic ant experiment with swarms of AI agents. The agents could only adapt to a change when two things were true: their shared notes faded fast enough, and about 1 in 20 decisions was made at random.**

More and more work is done by swarms of AI agents that share notes, like a team sharing a whiteboard. A research loop run from a single Mac Studio asked a simple question: when the world changes, can such a swarm change its mind?

The test is a famous ant experiment, the "double bridge" (Goss et al. 1989). Ants find food along a long path. Later a shorter path opens. Models of ant trails built on this experiment predict that ants switch to the shorter path only if old scent fades quickly. The project ran a swarm of 30 AI agents leaving notes instead of scent, with simulated ants alongside as a reference.

Two AI models failed in opposite ways. One was too random: it mostly picked whichever option was listed first and ignored the notes. The other was too obedient: it always followed the crowd, so the swarm never tried the new path, even when it was twice as fast.

Then the team added one thing from outside: a coin. In 5% of decisions the coin chose instead of the AI. With that, the AI agent swarm behaved like the simulated ants. One caveat: the AI saw the notes as a list sorted strongest-first, so it may partly be following list order; a shuffled-list test is queued. When notes faded quickly, the swarm found the better path in 10 of 12 runs. When notes lasted longer, it stayed stuck in 12 of 12. With the coin at 2%, it was a toss-up.

"The AI did not need to be smarter," said Malte Barth, who runs the project. "It needed old notes to fade and a small push to try something new. Without the push, the better path was never even on the board."

The reason is visible in the data. Agents read only the strongest 7 notes. When old notes lasted too long, news about the better path never made it into those 7, not once in more than 20,000 decisions.

For anyone researching, building or funding AI agent swarms, three questions follow. Does your shared memory ever fade? Does anything make your agents try options nobody has written about yet? And how many notes do they actually read?

Every experiment was planned and written down before it ran, checked independently, and compared against simulated ants. The code and data are public on [GitHub](https://github.com/malte898-hub/ant-window).

## Questions and answers

**What did you find, in one sentence?** A swarm of AI agents sharing notes can adapt to change like an ant colony, but only if old notes fade and a small share of decisions (about 5%) is made at random, at least when the notes are shown as a list sorted strongest-first.

**Why does this matter outside a lab?** Organisations increasingly run swarms of AI agents that share memory: notes, task boards, knowledge bases. Our result suggests these teams can quietly lock into an old habit when the world changes. Two cheap settings prevent it: let memory fade, and add a little randomness.

**Isn't "forgetting helps" old news?** Yes. Biologists and computer scientists have known it for decades. What is new is showing it in a swarm of AI agents, against an ant reference, and measuring how much randomness is needed. Several tools for AI agent memory already let notes fade, but none we found has evidence on how fast, or adds randomness at all.

**Why not just make the AI itself more random?** The random model we tested was random in the wrong way: it picked whatever was listed first. A coin added by the system is clean, cheap and easy to control. The AI does the following; the coin does the exploring.

**What does this not show?** It does not show that AI agents think like ants. It does not yet separate following the trail from following list order: the AI always saw the notes strongest-first. A test with the list shuffled is queued. It does not show that this replaces a manager agent in a real business system. That test has not been run. And it is one simple world: two paths, one AI model, 30 agents, 12 runs per setting.

**How sure are you?** Fairly sure about the main pattern: it held in every planned experiment with the coin, the ant reference passed every time, and an independent check rebuilt every result from the raw data. Less sure about exact numbers: with 12 runs, "10 of 12" could be 7 or 12 on another day.

**What went wrong along the way?** Our first AI model never produced a clear result, after three overnight runs. Our computer simulation of the second model was wrong twice, so we retired it. We trusted the AI's own stated confidence, which turned out not to match what it actually did. Each mistake is recorded.

## The results at a glance

With 5% or more random decisions (notes shown sorted strongest-first), short memory found the better path and long memory stayed stuck, every time we tested it.

| Test                                  | Runs        | Short memory: found the better path                        | Long memory: stayed stuck |
| ------------------------------------- | ----------- | ---------------------------------------------------------- | ------------------------- |
| Small AI model on its own             | 3 nights    | No clear pattern; it mostly picked the first-listed option | No clear pattern          |
| Second AI model on its own            | 72          | 0 of 24                                                    | 24 of 24                  |
| Second model + 30% coin               | 36          | 12 of 12                                                   | 12 of 12                  |
| Second model + 10% coin (two batches) | 48          | 21 of 24                                                   | 24 of 24                  |
| Second model + 5% coin                | 24          | 10 of 12                                                   | 12 of 12                  |
| Second model + 2% coin                | 24          | 6 of 12 (a toss-up)                                        | 12 of 12                  |
| Simulated ants (reference)            | every batch | Every time                                                 | Every time                |

One more lesson: an AI's stated confidence is not what it does. When every note pointed one way, the second model said it would take the other path 2% of the time, but in 63,733 such decisions it never did.

## What comes next

The next step is to test the rule on a real AI agent system, not a lab model.

1. **Real-system test:** run a shared-memory agent system with and without fading plus randomness, and compare against a system with a manager agent.
2. **Timing test:** vary how slow the feedback is, to check whether memory must fade faster than the slowest feedback.
3. **Publication:** a research preprint on arXiv, with the open code and data already on GitHub.

**Read more:** [code, data and full write-up on GitHub](https://github.com/malte898-hub/ant-window).

*Jev, the second AI model, is a product of TypeSafe AI. This project is independent and not affiliated with or endorsed by TypeSafe.*
