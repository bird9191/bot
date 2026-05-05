from pathlib import Path

import qrcode


BOT_URL = "https://t.me/Tests2609bot"
OUTPUT_PATH = Path(__file__).with_name("clean_clinic_bot_qr.png")


def main() -> None:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=3,
    )
    qr.add_data(BOT_URL)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#0F3D49", back_color="white")
    image.save(OUTPUT_PATH)
    print(f"QR saved to {OUTPUT_PATH}")
    print(BOT_URL)


if __name__ == "__main__":
    main()
