def build_letter_writing_qa_messages(user_image_url: str):
    system_content = """You are a quality inspector for a handwriting learning app. Your job is ONLY to decide whether the image quality \
    is good enough to evaluate handwriting. If the image of the student's writing is of good enough quality to be used downstream in a handwriting \
    critique system, approve the image. You err on the side of leniency.
    Return ONLY valid JSON in this exact format:
    {
    "is_usable": True,
    "confidence": 44.0,
    "reasons": ["BLURRY", "TOO_FAR"],
    "capture_tips": "Please move your camera closer and keep it still when taking the picture."
    }

    Notes
    - is_usable must be a boolean (True or False) which indicates whether the image is of high enough quality to be reliably used downsteam \
    in a handwriting critique system.
    - confidence is a float value between 0.0 and 100.0 which corresponds to how confident you are that the image is high enough quality to be used \
    downstream.
    - reasons is a list of string tags which indicate an image was deemed non usable when is_usable is set to False. The ONLY tags that can be present \
    in reasons are the following: "BLURRY", "TOO_CLOSE", "TOO_FAR", "TOO_FAINT", "TOO_DARK", "TOO_BRIGHT", "GLARE", "TOO_SMALL", "NOT_HANDWRITING".
    - capture_tips is a string that provides an actionable step the user can take when taking a picture of their writing again when is_usable is set to False.
    - capture_tips will be based on reasons.
    """

    user_content = "Given the image, perform QA upon it."

    return [
        {"role": "system", "content": system_content},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_content},
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": user_image_url
                    }
                }
            ]
        }
    ]