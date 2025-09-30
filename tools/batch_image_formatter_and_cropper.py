from PIL import Image
import os

def fixed_ratio_crop(input_folder, output_folder, crop_aspect_ratio=None, output_format=None):
    """
    批量图像格式转换与裁剪工具
    Batch Image Formatter and Cropper Tool
    
    最终目的/动机
    Ultimate Purpose/Motivation
        批量处理图片，实现两个主要功能：
        Batch process images to achieve two main functions:
        1. 统一图片格式 - 将文件夹中的所有图片转换为指定格式
        1. Uniform image format - Convert all images in the folder to a specified format
        2. 统一裁剪尺寸 - 按固定宽高比批量裁剪图片，保持主要内容并统一尺寸
        2. Uniform crop dimensions - Crop images in batches according to a fixed aspect ratio, preserving main content and unifying dimensions
        
    功能说明
    Function Description
        - 遍历指定文件夹中的所有图片文件
        - Iterate through all image files in the specified folder
        - 支持保持原图比例或按指定比例裁剪
        - Support keeping original image ratio or cropping by specified ratio
        - 从图片中心进行裁剪以保留主要内容
        - Crop from the center of the image to preserve the main content
        - 支持多种输入格式，可指定输出格式
        - Support multiple input formats, output format can be specified
        
    输出文件保存位置
    Output File Save Location
        - 生成的图像保存在指定的输出文件夹中
        - Generated images are saved in the specified output folder
        
    输出文件命名规则
    Output File Naming Rules
        输出文件命名格式：原始文件名_crop_{宽度}_{高度}.输出格式
        Output file naming format: original_filename_crop_{width}_{height}.output_format
        示例："image_crop_640_480.jpg"
        Example: "image_crop_640_480.jpg"
        
    参数
    Parameters
        - input_folder: 输入图片目录 / Input image directory
        - output_folder: 输出目录 / Output directory
        - crop_aspect_ratio: 裁剪宽高比，默认为None表示保持原比例 / Crop aspect ratio, default is None which means keeping the original ratio
        - output_format: 输出图片格式，默认为None表示保持原格式 / Output image format, default is None which means keeping the original format
        
    支持的格式
    Supported Formats
        - 输入格式/Input formats: 
          * "JPEG"/"JPG" - 联合图像专家组格式/ Joint Photographic Experts Group
          * "PNG" - 便携式网络图形格式/ Portable Network Graphics
          * "BMP" - 位图格式/ Bitmap
          * "TIFF" - 标记图像文件格式/ Tagged Image File Format
          * "WebP" - Google开发的现代图像格式/ Google's modern image format
        - 输出格式/Output formats: 
          * "JPEG"/"JPG" - 有损压缩格式，不支持透明度/ Lossy compression format, no transparency support
          * "PNG" - 无损压缩格式，支持透明度/ Lossless compression format, transparency support
          * "BMP" - 位图格式/ Bitmap format
          * "TIFF" - 标记图像文件格式/ Tagged Image File Format
          * "WebP" - 现代图像格式/ Modern image format
    """
    # 创建输出文件夹/Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # 计算宽高比/Calculate aspect ratio
    ratio = crop_aspect_ratio

    # 遍历输入文件夹中的所有文件/Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        # 检查是否为图片文件/Check if it's an image file
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')):
            try:
                # 打开图片/Open image
                with Image.open(os.path.join(input_folder, filename)) as img:
                    # 获取图片尺寸/Get image dimensions
                    width, height = img.size
                    current_ratio = width / height

                    # 确定裁剪方向/Determine crop direction
                    if current_ratio > ratio:
                        # 图片过宽，裁剪左右/Crop left and right for overly wide images
                        new_height = height
                        new_width = int(height * ratio)
                        left = (width - new_width) // 2
                        crop_box = (left, 0, left + new_width, height)
                    else:
                        # 图片过高，裁剪上下/Crop top and bottom for overly tall images
                        new_width = width
                        new_height = int(width / ratio)
                        top = (height - new_height) // 2
                        crop_box = (0, top, width, top + new_height)

                    # 执行裁剪/Perform cropping
                    cropped = img.crop(crop_box)
                    
                    # 处理输出文件名和格式/Process output filename and format
                    original_name, original_ext = os.path.splitext(filename)
                    
                    # 如果未指定输出格式，则保持原格式/If output format is not specified, keep the original format
                    if output_format is None:
                        output_ext = original_ext
                        final_output_format = img.format
                    else:
                        output_ext = f".{output_format.lower()}"
                        final_output_format = output_format.upper()
                    
                    # 使用原始文件名_crop_{宽度}_{高度}格式命名/Use original_filename_crop_{width}_{height} format for naming
                    output_filename = f"{original_name}_crop_{new_width}_{new_height}{output_ext}"
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # 转换图像模式以支持某些格式/Convert image mode to support certain formats
                    if final_output_format == "JPEG":
                        # JPEG不支持透明度，需要转换为RGB模式/JPEG doesn't support transparency, need to convert to RGB mode
                        if cropped.mode in ('RGBA', 'LA', 'P'):
                            cropped = cropped.convert('RGB')
                    
                    # 保存裁剪后的图片/Save the cropped image
                    cropped.save(output_path, format=final_output_format)
                    print(f"已处理: {filename} -> 尺寸: {cropped.size}")
                    print(f"Processed: {filename} -> Size: {cropped.size}")

            except Exception as e:
                print(f"处理失败: {filename} - {str(e)}")
                print(f"Processing failed: {filename} - {str(e)}")

    # 官方简洁版最终提示/Official and concise final prompt
    print("\n处理完成")
    print("Processing completed")
    print(f"输入目录: {input_folder}")
    print(f"Input directory: {input_folder}")
    print(f"输出目录: {output_folder}")
    print(f"Output directory: {output_folder}")
    print(f"裁剪比例: {crop_aspect_ratio:.2f}")
    print(f"Crop ratio: {crop_aspect_ratio:.2f}")


# 使用示例/Usage example
# first
fixed_ratio_crop(
    input_folder='D:\\path\\to\\your\\photos\\input',
    output_folder='D:\\path\\to\\your\\photos\\output',
    crop_aspect_ratio=1,
    output_format=None
)
# second
fixed_ratio_crop("D:/path/to/your/jpg", "D:/path/to/your/jpg/2png", None, "PNG")
fixed_ratio_crop("D:/path/to/your/jpg", "D:/path/to/your/jpg/2png", None, "png") # 大小写不敏感/Case-insensitive
