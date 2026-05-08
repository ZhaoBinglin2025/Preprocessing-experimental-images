import os
import sys
from PIL import Image

# ================== 配置区 ==================
INPUT_DIR = r"D:\PHD\unity3d\psych\PaoKu\practice"
OUTPUT_DIR = r"D:\PHD\unity3d\psych\PaoKu\practice_processed_sec"

TARGET_SIZE = 300      # 主体最长边
FINAL_PADDING = 10     # 四周额外透明边
ALPHA_THRESHOLD = 40   # Alpha阈值
# ===========================================


def trim_scale_and_pad(input_path, output_path,
                       target_size=300,
                       final_padding=10,
                       threshold=40):
    """裁剪透明边缘 -> 等比例缩放 -> 居中补齐300x300 -> 外扩10透明边"""

    try:
        # 1. 打开图片
        img = Image.open(input_path).convert("RGBA")

    except Exception as e:
        print(f"❌ 无法打开图片: {input_path}, 错误: {e}")
        return

    # 2. 获取 Alpha 通道
    alpha = img.getchannel("A")

    # 3. 过滤低透明像素
    filtered_alpha = alpha.point(
        lambda x: 0 if x <= threshold else x
    )

    # 4. 获取有效区域 bbox
    bbox = filtered_alpha.getbbox()

    if bbox is None:
        print(f"⚠️ 图片完全透明，跳过: {input_path}")
        return

    # 5. 裁剪有效区域
    img_cropped = img.crop(bbox)

    # 原始有效区域尺寸
    orig_w, orig_h = img_cropped.size

    # 6. 等比例缩放
    longest_side = max(orig_w, orig_h)
    scale_factor = target_size / longest_side

    new_w = int(round(orig_w * scale_factor))
    new_h = int(round(orig_h * scale_factor))

    img_resized = img_cropped.resize(
        (new_w, new_h),
        Image.LANCZOS
    )

    # ==================================================
    # 第一步：补齐到 300x300
    # ==================================================

    canvas_300 = Image.new(
        "RGBA",
        (target_size, target_size),
        (0, 0, 0, 0)
    )

    # 居中位置
    paste_x = (target_size - new_w) // 2
    paste_y = (target_size - new_h) // 2

    canvas_300.paste(
        img_resized,
        (paste_x, paste_y),
        img_resized
    )

    # ==================================================
    # 第二步：整体外扩50px透明边
    # 最终尺寸：400x400
    # ==================================================

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

    # 7. 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final_canvas.save(output_path, "PNG")

    print(
        f"✅ {os.path.basename(input_path)} | "
        f"原始: ({orig_w},{orig_h}) -> "
        f"缩放: ({new_w},{new_h}) -> "
        f"最终: ({final_size},{final_size})"
    )


def main():

    if not os.path.isdir(INPUT_DIR):
        print(f"❌ 输入目录不存在: {INPUT_DIR}")
        sys.exit(1)

    supported_ext = ('.png', '.webp', '.jpg', '.jpeg')

    processed_count = 0

    print("🚀 开始处理图片...")
    print(f"📏 主体最长边: {TARGET_SIZE}px")
    print(f"🪟 最终额外边距: {FINAL_PADDING}px")
    print(f"🎯 最终输出尺寸: {TARGET_SIZE + FINAL_PADDING * 2}px")
    print(f"🧼 Alpha阈值: {ALPHA_THRESHOLD}")

    for root, dirs, files in os.walk(INPUT_DIR):

        for file in files:

            if file.lower().endswith(supported_ext):

                input_path = os.path.join(root, file)

                # 保持目录结构
                rel_path = os.path.relpath(
                    input_path,
                    INPUT_DIR
                )

                output_path = os.path.join(
                    OUTPUT_DIR,
                    rel_path
                )

                # 强制输出PNG
                output_path = os.path.splitext(output_path)[0] + ".png"

                trim_scale_and_pad(
                    input_path,
                    output_path,
                    TARGET_SIZE,
                    FINAL_PADDING,
                    ALPHA_THRESHOLD
                )

                processed_count += 1

    print("\n🎉 全部完成！")
    print(f"📂 总计处理: {processed_count} 张图片")
    print(f"📍 输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()