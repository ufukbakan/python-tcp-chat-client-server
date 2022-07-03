class Message:
    def __init__(self, sender, receiver, content) -> None:
        self.sender = sender
        self.receiver = receiver
        self.content = content

def rowsToLines(rows:list) -> str:
    chatlog = rowsToStrings(rows)
    return "\n".join(chatlog)

def rowsToStrings(rows:list) -> list:
    return list(map(rowToMessageStr, rows))

def rowToMessageStr(row:tuple) -> str:
    return "%s: %s" % (row[0], row[2])

def filterRows(rows:list, keyword:str) -> list:
    result = []
    for row in rows:
        if(keyword in row[0] or keyword in row[2]):
            result.append(row)
    return result