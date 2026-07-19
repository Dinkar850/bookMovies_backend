class UserMessages:
    REGISTERED = "User registered successfully"
    LOGGED_IN = "User logged in successfully"
    LOGGED_OUT = "User logged out successfully"


class UserErrors:
    MISSING_REFRESH_TOKEN = "Missing refresh token in cookie"
    INVALID_REFRESH_TOKEN = "Given refresh token is invalid, blacklisted or expired"
