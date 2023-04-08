from fastapi import HTTPException


def not_authorized():
    return HTTPException(status_code=401, detail="Not authorized")


def forbidden():
    return HTTPException(status_code=403, detail="Forbidden")


def not_found(thing: str = ""):
    if thing == "":
        return HTTPException(status_code=404, detail="Not Found")
    else:
        return HTTPException(status_code=404, detail=f"{thing} not found.")
