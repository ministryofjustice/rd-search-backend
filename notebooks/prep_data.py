"""
Prepare data from a json file to use to try out Haystack functions.
"""


def replace_newlines(project_list: list[dict[str, any]]):
    """
    Replace newlines as they interfere with the matching
    """

    project_list = [
        {
            k: v.replace("\n", " ") if isinstance(v, str) else v
            for k, v in project.items()
        }
        for project in project_list
    ]

    return project_list


def format_doc_dict(doc: dict, field: str):
    """
    Reformat data into format accepted by Haystack.
    Here we may wish to search over multiple fields, so we include the text from different
    fields in separate dictionaries within a list.

    Args
    :doc: dictionary containing text data to search along with accompanying metadata
    :field: string corresponding to one of the dictionary keys, to indicate the field to index the text from
    """

    content = doc[field]

    if content is None:
        # We can't index None values, so returning None here allows us to skip fields where no info is provided
        return None
    elif isinstance(content, str) and (content.strip() == ""):
        # Also skip fields containing empty strings
        return None
    else:
        meta = doc.copy()

        meta["db_id"] = f"{meta['id']}"
        meta.pop("id")

        meta["matched_field"] = field

        doc_dict = {
            "meta": meta,
            "content": content,
        }

        return doc_dict


def prep_project_data(project_list: list[dict[str, any]]):
    """
    Iterate over a list of projects and apply _format_doc_dict().
    Here we wish to search over multiple fields, so we include the text from different
    fields in separate dictionaries within a list.

    Args:
        :project_list: A list of dictionaries containing text data to search along with accompanying metadata

    Returns:
        A reformated list of dictionaries, where different fields to search appear in their own dictionary.
    """

    # If the data contains multiple fields we'd want to search over, list them here
    fields_to_search = [
        "name",
        "description",
        "reasons_for_use",
        "problems_solved",
        "metrics",
    ]

    dataset = [
        y
        for project in project_list
        for field in fields_to_search
        if (y := format_doc_dict(project, field)) is not None
    ]

    return dataset
