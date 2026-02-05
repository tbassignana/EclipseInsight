import io

import qrcode
from qrcode.image.styledpil import StyledPilImage


def generate_qr_code(url: str, size: int = 10, border: int = 4) -> bytes:
    """Generate a QR code PNG image for the given URL.

    Args:
        url: The URL to encode in the QR code.
        size: Box size (pixels per module). Controls overall image size.
        border: Border width in modules (minimum 4 per QR spec).

    Returns:
        PNG image bytes.
    """
    qr = qrcode.QRCode(
        version=None,  # Auto-detect version based on data length
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=max(border, 1),
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
