import os
import sys
from PIL import Image

# ================== personalize your file path and size your experiment demand ==================
INPUT_DIR = r"your original path here"
OUTPUT_DIR = r"your processed path here"

TARGET_SIZE = 300      # This is to define the uniform longest side of all the picture pixels you want.
FINAL_PADDING = 10     # This is to define the edge pixels you want outside the main square.
ALPHA_THRESHOLD = 40   # Alpha threshold 
# ===========================================


def trim_scale_and_pad(input_path, output_path,
                       target_size=300,
                       final_padding=10,
                       threshold=40):
    

    try:
      
        img = Image.open(input_path).convert("RGBA")

    except Exception as e:
        print(f"unable to open file: {input_path}, error: {e}")
        return

   
    alpha = img.getchannel("A")

 
    filtered_alpha = alpha.point(
        lambda x: 0 if x <= threshold else x
    )

    
    bbox = filtered_alpha.getbbox()

    if bbox is None:
        print(f"the picture is all transparent，pass: {input_path}")
        return

  
    img_cropped = img.crop(bbox)

    
    orig_w, orig_h = img_cropped.size

   
    longest_side = max(orig_w, orig_h)
    scale_factor = target_size / longest_side

    new_w = int(round(orig_w * scale_factor))
    new_h = int(round(orig_h * scale_factor))

    img_resized = img_cropped.resize(
        (new_w, new_h),
        Image.LANCZOS
    )

  

    canvas_300 = Image.new(
        "RGBA",
        (target_size, target_size),
        (0, 0, 0, 0)
    )

   
    paste_x = (target_size - new_w) // 2
    paste_y = (target_size - new_h) // 2

    canvas_300.paste(
        img_resized,
        (paste_x, paste_y),
        img_resized
    )



    final_size = target_size + final_padding * 2

    final_canvas = Image.new(
        "RGBA",
        (final_size, final_size),
        (0, 0, 0, 0)
    )

    final_canvas.paste(
        canvas_300,
        (final_padding, final_padding),
        canvas_300
    )

    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final_canvas.save(output_path, "PNG")

    print(
        f"✅ {os.path.basename(input_path)} | "
        f"original: ({orig_w},{orig_h}) -> "
        f"zoom: ({new_w},{new_h}) -> "
        f"final: ({final_size},{final_size})"
    )


def main():

    if not os.path.isdir(INPUT_DIR):
        print(f"the input path doesn't exist: {INPUT_DIR}")
        sys.exit(1)

    supported_ext = ('.png', '.webp', '.jpg', '.jpeg')

    processed_count = 0

    print("🚀 start...")
    print(f"📏 Longest side of main body: {TARGET_SIZE}px")
    print(f"🪟 Final extra margin: {FINAL_PADDING}px")
    print(f"🎯 Final output size: {TARGET_SIZE + FINAL_PADDING * 2}px")
    print(f"🧼 Alpha threshold: {ALPHA_THRESHOLD}")

    for root, dirs, files in os.walk(INPUT_DIR):

        for file in files:

            if file.lower().endswith(supported_ext):

                input_path = os.path.join(root, file)


                rel_path = os.path.relpath(
                    input_path,
                    INPUT_DIR
                )

                output_path = os.path.join(
                    OUTPUT_DIR,
                    rel_path
                )

  
                output_path = os.path.splitext(output_path)[0] + ".png"

                trim_scale_and_pad(
                    input_path,
                    output_path,
                    TARGET_SIZE,
                    FINAL_PADDING,
                    ALPHA_THRESHOLD
                )

                processed_count += 1

    print("\n🎉 all done ！")
    print(f"📂 processed: {processed_count} pictures")
    print(f"📍 output path: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
