import os
import requests
import cairosvg

# --- Configuration ---
BASE_URL = "https://raw.githubusercontent.com/ornicar/lila/master/public/piece/merida/"
OUTPUT_DIR = "assets/images"

# Mapping from our desired filenames to the Lichess repo filenames
PIECE_MAP = {
    'w_pawn.png': 'wP.svg',
    'w_rook.png': 'wR.svg',
    'w_knight.png': 'wN.svg',
    'w_bishop.png': 'wB.svg',
    'w_queen.png': 'wQ.svg',
    'w_king.png': 'wK.svg',
    'b_pawn.png': 'bP.svg',
    'b_rook.png': 'bR.svg',
    'b_knight.png': 'bN.svg',
    'b_bishop.png': 'bB.svg',
    'b_queen.png': 'bQ.svg',
    'b_king.png': 'bK.svg',
}

def setup_assets():
    """
    Downloads chess piece SVG files from the Lichess GitHub repository,
    converts them to PNG, and saves them in the assets/images directory.
    """
    print("Setting up image assets...")

    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created directory: {OUTPUT_DIR}")

    for png_name, svg_name in PIECE_MAP.items():
        svg_url = f"{BASE_URL}{svg_name}"
        output_path = os.path.join(OUTPUT_DIR, png_name)

        try:
            # Download the SVG file
            print(f"Downloading {svg_url}...")
            response = requests.get(svg_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            svg_content = response.content

            # Convert SVG to PNG
            print(f"Converting {svg_name} to {png_name}...")
            cairosvg.svg2png(bytestring=svg_content, write_to=output_path)

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {svg_url}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {svg_name}: {e}")

    print("\nAsset setup complete!")
    print(f"All piece images should now be in the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    setup_assets()
