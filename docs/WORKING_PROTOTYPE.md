# Working Prototype Snapshot

Status: working local prototype, frozen at v0.4.2 on August 16, 2026.

This document records the version worth demonstrating before further development. It is not presented as a finished NPC simulation. The important result is that a player can speak freely to a Stardew Valley character, receive a locally generated in-character reply, and carry relationship context into later exchanges.

## What the demo proves

```text
Player types a message in Stardew Valley
  -> the SMAPI mod collects the nearby NPC and game context
  -> NPCBridge loads that character's profile and relationship history
  -> the local Qwen model judges and answers the message
  -> NPCBridge validates and saves the result
  -> Stardew displays the expression and dialogue
```

No cloud AI service is required. Stardew Valley, NPCBridge, Ollama, the model, character profiles, and relationship data all run on the same Windows PC.

## Demonstration setup

- Stardew Valley
- SMAPI
- NPCBridge 0.4.2
- Ollama
- `qwen3:4b-instruct-2507-q4_K_M`
- Supported characters: Linus and Abigail
- Conversation key: `Alt+0`

Start the system from the project folder:

```powershell
.\scripts\start-system.ps1
```

Launch the game through `StardewModdingAPI.exe` in your own Stardew Valley folder. Load a save, stand within four tiles of Linus or Abigail, press `Alt+0`, type a message, and press Enter. Escape cancels text entry or a request in progress.

## Suggested live demo

Linus is the easiest character to find consistently because he is usually near his tent in the mountains.

1. Begin with a normal greeting or question.
2. Give him a sincere compliment and observe a positive reply.
3. Add an insult to a compliment, such as `what a beautiful idiot you are`, and observe that he notices the insult instead of accepting the praise.
4. Ask what was previously said. He should refer to recent conversation history.
5. Apologize. If the relationship is already very negative, he should remember the pattern and remain guarded instead of forgiving immediately.
6. Close the dialogue, open another conversation, and verify that recent events and the relationship score persist.

The exact wording is generated and will vary. The behavior and remembered context are the parts being demonstrated.

## Working use cases

### Character-specific conversation

The player can write ordinary language instead of choosing a fixed dialogue option. Linus and Abigail use separate external profiles, giving them different backgrounds, vocabulary, cadence, habits, and reactions.

### Mixed-intent messages

A message can contain both praise and an insult. The model receives the complete message and relationship context, so it can respond to the mixed intent instead of relying only on a single keyword.

### Hostility and escalation

Direct insults, repeated profanity, and threats can produce offended or guarded reactions. Continued negative interaction lowers the persistent relationship score, allowing later replies to become less patient and more confrontational.

### Memory and grudges

NPCBridge stores completed exchanges and supplies recent history to the model. A character can recall earlier insults when the player asks what happened or tries to change tone.

### Apology after repeated insults

An apology does not automatically erase prior behavior. At a very negative relationship stage, the NPC can acknowledge it while remaining distrustful. This demonstrates memory affecting the present response, although gradual reconciliation still needs refinement.

### Positive relationship changes

Messages judged positive can raise the bridge relationship score and Stardew friendship. Repeated praise is intended to feel less effective than a sincere isolated compliment, though positive-stage variation remains less convincing than hostile-stage variation.

### Safe game integration

Model generation runs outside Stardew's main thread. The game shows a waiting state, and the request can be cancelled. Interaction IDs prevent cancelled or stale replies from modifying relationship state.

## What is working reliably

- Opening, submitting, and cancelling the in-game text box
- Finding the nearest supported NPC
- Passing game and character context to a standalone local service
- Generating and displaying dialogue plus a facial-expression description
- Structured POSITIVE, NEUTRAL, or NEGATIVE outcomes
- Persistent per-player, per-character relationship state
- Recent conversation recall
- Mixed praise/insult recognition
- Stronger hostile-stage responses and refusal to forget repeated abuse immediately
- Duplicate, cancelled, stale, and failed interaction protection
- Source and packaged bridge operation

## Current limitations

- Responses are generated on CPU. A cold request can take roughly 35–55 seconds; warmed requests have commonly taken about 7–10 seconds in local tests.
- The model occupies about 3 GB of RAM while loaded.
- Generated wording is nondeterministic, so an occasional reply may be too short, repetitive, or weaker than the relationship state suggests.
- Reconciliation is currently too rigid at very negative scores. Multiple apologies may receive similar dismissive replies instead of showing small, believable movement.
- Negative-stage behavior is more distinct than positive-stage behavior.
- Sentiment uses only three outcomes, with fixed configured score changes.
- Only Linus and Abigail have profiles.
- Facial expressions are written as text; portraits and character animations do not change.
- There is no voice, autonomous NPC action, quest generation, or multiplayer support.

## Verification recorded for this snapshot

- 25 automated bridge tests passed.
- The Release Stardew mod built successfully.
- The packaged NPCBridge health endpoint reported version 0.4.2.
- Protocol versions 1.0 and 2.0 were available.
- Qwen was preloaded with a 3072-token context and 30-minute keep-alive.
- Player-controlled in-game conversations demonstrated insults, mixed messages, recall, guarded apologies, persistent tone, and expression text.

## Frozen scope

This snapshot should remain the reference demo while attention moves to another project. No model, prompt, score, memory, or adapter changes should be made merely to polish the demo. Future work should begin from a Git checkpoint and compare behavior against the use cases above.

Nothing has been pushed as part of this documentation pass.
