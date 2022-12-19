def correct_team_name(team_name):
    """GH team names cannot have a full dot or
    space in them replace with -

    Args:
        team_name (string): the name of the team
    """
    new_team_name = ""
    if team_name.startswith("."):
        temp_name = team_name[len("."):]
        temp_name = temp_name.replace(".", "-")
        new_team_name = temp_name.replace(" ", "-")
        return new_team_name
    else:
        temp_name = team_name.replace(".", "-")
        new_team_name = temp_name.replace(" ", "-")
    return new_team_name


print("Start")
print(correct_team_name(".jit-admin team"))
print(correct_team_name("LAA get access"))
print("Finished")
