import io
import zipfile
from pathlib import Path

from PIL import Image


VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def generate_thumbnails_from_zip(
    zip_filepath: str | Path,
    output_dir: str | Path,
    thumbnail_size: tuple[int, int] = (128, 128),
) -> None:
    """
    Extract images from a zip file, generate thumbnails, and save them to an
    output directory.
    """
    zip_path = Path(zip_filepath).expanduser()
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            print(f"Opening archive: {zip_path}...\n")

            for file_info in archive.infolist():
                if file_info.is_dir():
                    continue

                filename = file_info.filename
                extension = Path(filename).suffix.lower()
                if extension not in VALID_IMAGE_EXTENSIONS:
                    continue

                try:
                    image_data = archive.read(filename)
                    with Image.open(io.BytesIO(image_data)) as image:
                        if image.mode in ("RGBA", "P"):
                            image = image.convert("RGB")

                        image.thumbnail(thumbnail_size)
                        new_filename = f"thumb_{Path(filename).name}"
                        save_path = output_path / new_filename
                        save_format = "JPEG" if extension in {".jpg", ".jpeg"} else "PNG"
                        image.save(save_path, format=save_format)
                        print(f"Successfully created: {new_filename}")
                except (OSError, zipfile.BadZipFile) as exc:
                    print(f"Skipped {filename} - Error during processing: {exc}")

        print(f"\nProcess complete. Thumbnails are saved in: {output_path.resolve()}")
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid zip archive.")
    except FileNotFoundError:
        print(f"Error: '{zip_path}' was not found.")


if __name__ == "__main__":
    print("--- Zip to Thumbnails Generator ---")
    user_zip = input("Enter the full path to your zipped folder (.zip): ").strip().strip("\"'")
    user_output = input("Enter the desired path for the thumbnails folder: ").strip().strip("\"'")
    generate_thumbnails_from_zip(user_zip, user_output)
