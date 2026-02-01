class SlotErrors:
    BEFORE_NOW = "Slot is scheduled before the current date and time"
    BEFORE_MOVIE_RELEASE = (
        "Slot is scheduled for a date before its movie's release date"
    )
    INSUFFICIENT_DURATION = "Slot's duration is shorter than its movie's duration"
    INVALID_LANGUAGE = "Slot's language is not one of its movie's languages"
    OVERLAPS_PREVIOUS_SLOT = "Slot is scheduled before its previous slot has ended"
    OVERLAPS_NEXT_SLOT = "Slot is scheduled with an end time overlapping with the next slot for the entered duration"
