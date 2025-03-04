from drf_yasg import openapi


signup_docs = {
    'operation_description': """
    Multi-step user registration process.
    
    Step 1: Submit personal information
    - first_name: User's first name
    - last_name: User's last name 
    - phone_number: Valid phone number (format: +90XXXXXXXXXX)
    
    Step 2: Verify phone number (use /user/verify/phone/ endpoint)
    
    Step 3: Complete registration
    - username: Unique username
    - password: Strong password
    - password_confirm: Password confirmation
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (!@#$%^&*(),.?":{}|<>)
    
    Endpoint: /user/signup/
    """,
    'tags': ['user'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'step': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Current registration step (1 or 3)',
                enum=[1, 3]
            ),
            'first_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 1'
            ),
            'last_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 1'
            ),
            'phone_number': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 1 (format: +90XXXXXXXXXX)'
            ),
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Required for step 3 (received from step 1 response)'
            ),
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 3'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 3'
            ),
            'password_confirm': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Required for step 3'
            ),
        },
        required=['step']
    ),
    'responses': {
        201: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "status": "success",
                    "message": "Registration step completed",
                    "user_id": 123,
                    "next_step": 2,
                    "username_suggestions": ["john_doe", "john.doe", "johndoe123"]
                },
            }
        ),
        400: openapi.Response(
            description='Bad Request',
            examples={
                'application/json': {
                    "status": "error",
                    "message": "missing fields",
                },
            }
        ),
        500: openapi.Response(description='Server error'),
    },
    'security': [],
}


verify_phone_docs = {
    'operation_description': """
    Verify phone number with received verification code.
    
    Important notes:
    - Verification code expires after 3 minutes
    - Maximum 3 verification attempts allowed
    - After 3 failed attempts, new code must be requested
    
    Endpoint: /user/verify/phone
    """,
    'tags': ['user'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID received from signup step 1'
            ),
            'verification_code': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='6-digit verification code received via SMS'
            ),
        },
        required=['user_id', 'verification_code']
    ),
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "status": "success",
                    "message": "Phone verified successfully",
                    "user_id": 123,
                    "next_step": 3
                },
            }
        ),
        400: openapi.Response(
            description='Bad Request',
            examples={
                'application/json': {
                    "status": "error",
                    "message": "Invalid verification code"
                },
            }
        ),
        404: openapi.Response(description='User not found'),
        500: openapi.Response(description='Server error'),
    },
    'security': [],
}


resend_code_docs = {
    'operation_description': """
    Request a new verification code.
    
    - New code will be sent via SMS
    - Previous code becomes invalid
    - New code valid for 3 minutes
    - Verification attempts count is reset
    
    Endpoint: /user/resend/code
    """,
    'tags': ['user'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID received from signup step 1'
            )
        },
        required=['user_id']
    ),
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "message": "New verification code sent successfully"
                },
            }
        ),
        400: openapi.Response(description='Bad request'),
        404: openapi.Response(description='User not found'),
        500: openapi.Response(description='Server error'),
    },
    'security': [],
}


check_username_docs = {
    'operation_description': """
    Check if a username is available for registration.
    
    Username requirements:
    - 3-30 characters
    - Can contain letters, numbers, and underscore
    
    Endpoint: /user/check/username
    """,
    'tags': ['user'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Username to check'
            ),
        },
        required=['username']
    ),
    'responses': {
        200: openapi.Response(
            description='Username is available',
            examples={
                'application/json': {
                    "message": "Username is available"
                },
            }
        ),
        409: openapi.Response(
            description='Username exists',
            examples={
                'application/json': {
                    "message": "Username already exists"
                },
            }
        ),
        400: openapi.Response(description='Invalid username format'),
        500: openapi.Response(description='Server error'),
    },
    'security': [],
}


check_phone_docs = {
    'operation_description': """
    Check if a phone number is available for registration.
    
    Phone number format: +90XXXXXXXXXX
    
    Endpoint: /user/check/phone
    """,
    'tags': ['user'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone_number': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Phone number to check (format: +90XXXXXXXXXX)'
            ),
        },
        required=['phone_number']
    ),
    'responses': {
        200: openapi.Response(
            description='Phone number is available',
            examples={
                'application/json': {
                    "message": "Phone number is available"
                },
            }
        ),
        409: openapi.Response(
            description='Phone number exists',
            examples={
                'application/json': {
                    "message": "Phone number already exists"
                },
            }
        ),
        400: openapi.Response(description='Invalid phone number format'),
        500: openapi.Response(description='Server error'),
    },
    'security': [],
}


update_interests_docs = {
    'operation_description': """
    Update user interests.
    
    Requirements:
    - Maximum 3 interests allowed
    - Authentication required (Bearer token)
    - List of interest IDs (max 3)
    
    Endpoint: /user/interests/
    """,
    'tags': ['interests'],
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'interests': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
            )
        },
        required=['interests']
    ),
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "message": "Interests updated successfully",
                    "interests": ["Music", "Sports", "Technology"]
                },
            }
        ),
        400: openapi.Response(description='Invalid request'),
        401: openapi.Response(description='Authentication required'),
        500: openapi.Response(description='Server error'),
    },
    "security": [{"Bearer": []}],
}


update_pictures_docs = {
    'operation_description': """
    Update user profile and banner pictures.
    
    Requirements:
    - Authentication required (Bearer token)
    - Maximum file size: 5MB
    - Allowed formats: JPG, JPEG, PNG
    
    Endpoint: /user/pictures/
    """,
    'tags': ['user'],
    'manual_parameters': [
        openapi.Parameter(
            'profile_picture',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description='Profile picture file (jpg, jpeg, png)',
            required=False
        ),
        openapi.Parameter(
            'banner_picture', 
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description='Banner picture file (jpg, jpeg, png)',
            required=False
        ),
    ],
    'consumes': ['multipart/form-data'],
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "message": "Upload successful",
                    "profile_url": "https://bucket-name.s3.region.amazonaws.com/profile/user_123.jpg",
                    "banner_url": "https://bucket-name.s3.region.amazonaws.com/banner/user_123.jpg"
                },
            }
        ),
        400: openapi.Response(description='Invalid file format or size'),
        401: openapi.Response(description='Authentication required'),
        403: openapi.Response(description='Invalid token'),
        500: openapi.Response(description='Server error'),
    },
    "security": [{"Bearer": []}],
}


list_interests_docs = {
    'operation_description': """
    List all available interests.
    Endpoint: /user/interests/list/
    """,
    'tags': ['interests'],
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': {
                    "interests": [
                        {"id": 1, "name": "Music"},
                        {"id": 2, "name": "Sports"},
                        {"id": 3, "name": "Technology"}
                    ]
                },
            }
        ),
        500: openapi.Response(description='Server error'),
    }
}


get_suggestions_docs = {
    'operation_description': """
    Get suggested users.
    
    
    Endpoint: /user/suggestions/
    """,
    'tags': ['suggestions'],
    'responses': {
        200: openapi.Response(
            description='Success',
            examples={
                'application/json': [
                    {
                        "username": "next",
                        "first_name": "Next",
                        "last_name": "User",
                        "profile_picture": "profile/user_1.jpg",
                        "count_post": 0,
                        "count_followers": 0,
                        "count_following": 0
                    }
                ]
            }
        ),
        401: openapi.Response(description='Authentication required'),
        403: openapi.Response(description='Invalid token'),
        500: openapi.Response(description='Server error'),
    },
    "security": [{"Bearer": []}],
}

