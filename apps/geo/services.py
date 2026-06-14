import re

ADDRESS_PATTERN = re.compile(
    r'^[\w\s.,\-/\\\'"#ºª()\[\]àèéìòùÀÈÉÌÒÙáéíóúñüÁÉÍÓÚÑÜäöüßÄÖÜæøåÆØÅ\dа-яА-ЯёЁ]{5,}$'
)

MIN_ADDRESS_LENGTH = 5


def validate_address(address):
    if not address or not isinstance(address, str):
        return False, 'Address is required'
    address = address.strip()
    if len(address) < MIN_ADDRESS_LENGTH:
        return False, 'Address is too short (minimum 5 characters)'
    if not ADDRESS_PATTERN.match(address):
        return False, 'Address contains invalid characters'
    if not re.search(r'[\d]', address):
        return False, 'Address must contain a building/house number'
    return True, None