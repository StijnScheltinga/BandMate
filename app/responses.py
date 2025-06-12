unauthorized = {
    401: {
        "description": "Authentication error",
        "content": {
            "application/json": {
                "examples": {
					"NoToken": {
						"summary": "No token provided",
						"value": {"detail": "Not authenticated"}
					},
                    "ExpiredToken": {
                        "summary": "Access token expired",
                        "value": {"detail": "Access token expired"}
                    },
                    "InvalidToken": {
                        "summary": "Malformed token",
                        "value": {"detail": "Could not validate user"}
                    }
                }
            }
        }
    }
}
