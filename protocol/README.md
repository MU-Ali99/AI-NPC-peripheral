# Conversation Protocol v1

`POST /v1/conversation` accepts JSON using `conversation-v1.schema.json`. `/conversation` is a compatibility alias. Successful and handled-error responses both use HTTP 200 so a game adapter can safely display a user-facing message; malformed requests use HTTP 422.

NPCBridge binds to loopback by default. Change the host intentionally when moving it to peripheral hardware, and protect the network appropriately before doing so.

