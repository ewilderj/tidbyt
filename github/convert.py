import base64
import os
import sys

def png_to_html_src(image_path):
  """Converts a PNG image to a base64 encoded string suitable for use
  in an HTML <img> src attribute.

  Args:
    image_path: The path to the PNG image file.

  Returns:
    A string representing the base64 encoded image, or None if
    an error occurs.

  """
  try:
    with open(image_path, "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
      return f"data:image/png;base64,{encoded_string}"
  except FileNotFoundError:
    print(f"Error: File not found at {image_path}")
    return None
  except Exception as e:
    print(f"An error occurred: {e}")
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert.py <image_file.png>")
        sys.exit(1)

    image_file_path = sys.argv[1]

    if not os.path.isfile(image_file_path):
        print(f"Error: {image_file_path} is not a valid file.")
        sys.exit(1)

    if not image_file_path.lower().endswith(".png"):
        print(f"Error: {image_file_path} is not a PNG file.")
        sys.exit(1)

    html_src_string = png_to_html_src(image_file_path)

    if html_src_string:
        print(f'HTML src string: {html_src_string}')
        # Example HTML snippet:
        # print(f'<img src="{html_src_string}" alt="Embedded Image">')
    else:
        print("Could not generate HTML src string.")
