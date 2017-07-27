def get_command_type(command_tokens):
    if len(command_tokens) == 0:
        return None

    if "$" in command_tokens[0]:
        return "price"

    if command_tokens[0] == "buy":
        return "buy"

    if command_tokens[0] == "sell":
        return "sell"

    if command_tokens[0] == "balance":
        return "balance"

    if command_tokens[0] == "portfolio":
        return "portfolio"

    if command_tokens[0] in set(["leader", "leaderboard"]):
        return "leaderboard"

    if command_tokens[0] == "help":
        return "help"

    if command_tokens[0] in set(["hello", "hey", "greet", "hi"]):
        return "greet"

    if command_tokens[0] in set(["meme", "shit", "shitpost"]):
        return "meme"
