class SlotErrors:
    BEFORE_NOW = "Slot is scheduled before the current date and time"
    BEFORE_MOVIE_RELEASE = (
        "Slot is scheduled for a date before its movie's release date"
    )
    INVALID_DURATION = "Slot's duration is either negative or 0"
    INSUFFICIENT_DURATION = "Slot's duration is shorter than its movie's duration"
    INVALID_LANGUAGE = "Slot's language is not one of its movie's languages"
    OVERLAPPING_SLOT = (
        "Slot created is overlapping with an existing slot for the same cinema"
    )
