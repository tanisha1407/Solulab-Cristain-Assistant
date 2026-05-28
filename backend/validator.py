import re

# ==========================================
# SCRIPTURE REFERENCE REGEX
# ==========================================

SCRIPTURE_REGEX = r"""
\b
(?:[1-3]\s)?                 # Optional 1,2,3 prefix
[A-Z][a-zA-Z]+               # Book name
(?:\s[A-Z][a-zA-Z]+)?        # Optional second word
\s
\d+:\d+                      # Chapter:Verse
\b
"""

# ==========================================
# EXTRACT REFERENCES
# ==========================================

def extract_scripture_references(
    text: str
):
    """
    Extract scripture references
    from generated response.
    """

    matches = re.findall(
        SCRIPTURE_REGEX,
        text,
        re.VERBOSE
    )

    cleaned = []

    for match in matches:

        cleaned.append(
            match.strip()
        )

    return cleaned

# ==========================================
# VALIDATE REFERENCES
# ==========================================

def validate_references(
    response_text: str,
    valid_references: list
):
    """
    Detect hallucinated references.

    Args:
        response_text: LLM response
        valid_references: references retrieved from RAG

    Returns:
        invalid references list
    """

    found_refs = extract_scripture_references(
        response_text
    )

    invalid_refs = []

    valid_set = set(valid_references)

    for ref in found_refs:

        if ref not in valid_set:

            invalid_refs.append(ref)

    return invalid_refs

# ==========================================
# CHECK FAKE VERSE QUERY
# ==========================================

def is_fake_reference_query(
    user_query: str
):
    """
    Detect potentially fake scripture queries.

    Example:
    Genesis 51:2
    """

    refs = extract_scripture_references(
        user_query
    )

    if refs:
        return refs

    return []

# ==========================================
# SAFE RESPONSE HELPER
# ==========================================

def invalid_reference_response(
    invalid_refs
):
    """
    Generate user-facing warning
    for hallucinated scripture.
    """

    refs = ", ".join(invalid_refs)

    return (
        f"The following scripture references "
        f"could not be verified: {refs}. "
        f"Please check the citation."
    )

# ==========================================
# REMOVE DUPLICATES
# ==========================================

def remove_duplicate_references(
    references: list
):
    """
    Remove duplicate scripture references.
    """

    return list(set(references))

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    sample_response = """
    Jesus teaches love in John 3:16
    and forgiveness in Matthew 6:14.
    Some people incorrectly cite Genesis 51:2.
    """

    valid_refs = [
        "John 3:16",
        "Matthew 6:14"
    ]

    print("\n===== EXTRACTED REFERENCES =====\n")

    refs = extract_scripture_references(
        sample_response
    )

    print(refs)

    print("\n===== VALIDATION =====\n")

    invalid = validate_references(
        sample_response,
        valid_refs
    )

    print("Invalid References:")

    print(invalid)

    print("\n===== SAFE RESPONSE =====\n")

    if invalid:

        print(
            invalid_reference_response(
                invalid
            )
        )