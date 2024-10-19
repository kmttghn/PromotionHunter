import re

def text_to_float(self, text):
    """
    Find numeric text and returns as float

    :param text: A string to search for text
    :type text: string
    :return: The numbers in float type
    :rtype: float
    """
    if text:
        extract = re.search(r"(\d+\.?\d*)", text)
        return float(extract.group()) if extract else None
    return