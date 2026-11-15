SUBJECT_MARKER = "### Rewritten Subject ###"
BODY_MARKER = "### Rewritten Body ###"
NOTES_MARKER = "### Cultural Notes ###"


def parse_rewrite_response(content: str) -> tuple[str, str, str]:
    """Parse the three required sections returned by the rewrite model.

    Raises ValueError when the model returns an empty response, omits a
    section, changes the section order, or leaves a section empty.
    """
    if not isinstance(content, str) or not content.strip():
        raise ValueError("The rewrite response must be non-empty text.")

    subject_marker = content.find(SUBJECT_MARKER)
    body_marker = content.find(BODY_MARKER)
    notes_marker = content.find(NOTES_MARKER)

    if not (0 <= subject_marker < body_marker < notes_marker):
        raise ValueError(
            "The rewrite response is missing or misorders a required section."
        )

    subject_start = subject_marker + len(SUBJECT_MARKER)
    body_start = body_marker + len(BODY_MARKER)
    notes_start = notes_marker + len(NOTES_MARKER)

    subject = content[subject_start:body_marker].strip()
    body = content[body_start:notes_marker].strip()
    notes = content[notes_start:].strip()

    if not subject or not body or not notes:
        raise ValueError(
            "The rewrite response must contain all three non-empty sections."
        )

    return subject, body, notes
