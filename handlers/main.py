def get_command_type(command_tokens):
    if len(command_tokens) == 0:
        return None

    if "$" in command_tokens[0]:
        return "price"

    if command_tokens[0] == "buy":
        return "buy"

    if command_tokens[0] == "sell":
        return "sell"
