from .models import ConversationRequest


def build_prompt(request: ConversationRequest, profile: dict) -> tuple[str, str]:
    personality = ", ".join(profile["personality"])
    rules = "\n".join(f"- {rule}" for rule in profile["rules"])
    system = f"""You write one short line of in-game dialogue as {profile['displayName']} from Stardew Valley.
Personality: {personality}.
Speaking style: {profile['speakingStyle']}
Knowledge boundary: {profile['knowledgeBoundary']}
Rules:
{rules}
- Output dialogue only: no name label, quotation marks, stage directions, or analysis.
- Keep the answer under {profile['maximumCharacters']} characters.
"""
    user = f"""World: {request.world.season} day {request.world.day}, time {request.world.time}, weather {request.world.weather}, location {request.world.location}.
Relationship: {request.npc.friendshipHearts} friendship hearts with {request.player.name}.
{request.player.name} says: {request.player.message}"""
    return system, user

