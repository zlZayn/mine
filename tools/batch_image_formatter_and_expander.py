from PIL import Image
import os

def fixed_ratio_expand(input_folder, output_folder, target_aspect_ratio, background_color=(255, 255, 255), output_format=None):
    """
    批量图像格式转换与扩充工具
    Batch Image Formatter and Expander Tool
    
    最终目的/动机
    Ultimate Purpose/Motivation
        批量处理图片，实现两个主要功能：
        Batch process images to achieve two main functions:
        1. 统一图片格式 - 将文件夹中的所有图片转换为指定格式
        1. Uniform image format - Convert all images in the folder to a specified format
        2. 向外扩充尺寸 - 按固定宽高比批量扩充图片，保持原有内容不变并向外填充背景色
        2. Expand outward - Expand images in batches according to a fixed aspect ratio, keeping the original content and filling the background
        
    功能说明
    Function Description
        - 遍历指定文件夹中的所有图片文件
        - Iterate through all image files in the specified folder
        - 支持保持原图内容不变，向外扩充到指定比例
        - Support keeping original image content unchanged and expanding to specified ratio
        - 从图片中心进行扩充，将原图居中放置
        - Expand from the center of the image, placing the original image in the center
        - 支持自定义填充背景颜色
        - Support custom background color for filling
        - 支持多种输入格式，可指定输出格式
        - Support multiple input formats, output format can be specified
        
    输出文件保存位置
    Output File Save Location
        - 生成的图像保存在指定的输出文件夹中
        - Generated images are saved in the specified output folder
        
    输出文件命名规则
    Output File Naming Rules
        输出文件命名格式：原始文件名_expand_{宽度}_{高度}.输出格式
        Output file naming format: original_filename_expand_{width}_{height}.output_format
        示例："image_expand_800_600.jpg"
        Example: "image_expand_800_600.jpg"
        
    参数
    Parameters
        - input_folder: 输入图片目录 / Input image directory
        - output_folder: 输出目录 / Output directory
        - target_aspect_ratio: 目标宽高比 / Target aspect ratio
        - background_color: 填充背景颜色，默认为白色(255, 255, 255) / Background color for filling, default is white(255, 255, 255)
            支持三种颜色格式：
            Support three color formats:
                1. 英文颜色名称：如 'white', 'black', 'red' 等PIL库支持的标准颜色
                1. English color names: e.g. 'white', 'black', 'red' as supported by PIL library
                2. RGB元组：如 (255, 255, 255) 表示白色
                2. RGB tuple: e.g. (255, 255, 255) for white
                3. 十六进制字符串：如 '#FF0000' 表示红色
                3. Hexadecimal string: e.g. '#FF0000' for red
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

                    # 确定扩充后的尺寸/Determine expanded dimensions
                    if current_ratio > target_aspect_ratio:
                        # 原图更宽，扩充高度/Original image is wider, expand height
                        new_width = width
                        new_height = int(width / target_aspect_ratio)
                        # 计算原图放置位置/Calculate position to place original image
                        paste_y = (new_height - height) // 2
                        paste_x = 0
                    else:
                        # 原图更高，扩充宽度/Original image is taller, expand width
                        new_height = height
                        new_width = int(height * target_aspect_ratio)
                        # 计算原图放置位置/Calculate position to place original image
                        paste_x = (new_width - width) // 2
                        paste_y = 0

                    # 判断图片模式以支持透明度/Determine image mode to support transparency
                    if img.mode in ('RGBA', 'LA'):
                        # 对于带透明度的图片，使用RGBA模式/For images with transparency, use RGBA mode
                        expanded = Image.new('RGBA', (new_width, new_height), background_color + (255,))
                    else:
                        # 对于不透明图片，使用RGB模式/For opaque images, use RGB mode
                        expanded = Image.new('RGB', (new_width, new_height), background_color)

                    # 将原图粘贴到新画布中心/Paste the original image to the center of the new canvas
                    expanded.paste(img, (paste_x, paste_y))
                    
                    # 处理输出文件名和格式/Process output filename and format
                    original_name, original_ext = os.path.splitext(filename)
                    
                    # 如果未指定输出格式，则保持原格式/If output format is not specified, keep the original format
                    if output_format is None:
                        output_ext = original_ext
                        final_output_format = img.format
                    else:
                        output_ext = f".{output_format.lower()}"
                        # 确保格式名称与PIL兼容/Ensure format name is compatible with PIL
                        if output_format.lower() == 'jpg':
                            final_output_format = 'JPEG'
                        else:
                            final_output_format = output_format.upper()
                    
                    # 使用原始文件名_expand_{宽度}_{高度}格式命名/Use original_filename_expand_{width}_{height} format for naming
                    output_filename = f"{original_name}_expand_{new_width}_{new_height}{output_ext}"
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # 转换图像模式以支持某些格式/Convert image mode to support certain formats
                    if final_output_format == "JPEG":
                        # JPEG不支持透明度，需要转换为RGB模式/JPEG doesn't support transparency, need to convert to RGB mode
                        if expanded.mode in ('RGBA', 'LA', 'P'):
                            expanded = expanded.convert('RGB')
                    
                    # 保存扩充后的图片/Save the expanded image
                    expanded.save(output_path, format=final_output_format)
                    print(f"已处理: {filename} -> 尺寸: {expanded.size}")
                    print(f"Processed: {filename} -> Size: {expanded.size}")

            except Exception as e:
                print(f"处理失败: {filename} - {str(e)}")
                print(f"Processing failed: {filename} - {str(e)}")

    # 最终提示/Final prompt
    print("\n处理完成")
    print("Processing completed")
    print(f"输入目录: {input_folder}")
    print(f"Input directory: {input_folder}")
    print(f"输出目录: {output_folder}")
    print(f"Output directory: {output_folder}")
    print(f"目标比例: {target_aspect_ratio:.2f}")
    print(f"Target ratio: {target_aspect_ratio:.2f}")
    print(f"背景颜色: {background_color}")
    print(f"Background color: {background_color}")


# 使用示例/Usage example
# first
fixed_ratio_expand(
    input_folder="c:\\path\\to\\your\\gallery\\1",
    output_folder="c:\\path\\to\\your\\gallery\\2",
    target_aspect_ratio=4/3,
    background_color='#2181A1'
)
# second
fixed_ratio_expand(
    input_folder='d:\\path\\to\\your\\favorite_img\\img',
    output_folder='d:\\path\\to\\your\\favorite_img\\png',
    target_aspect_ratio=9/16,
    background_color=(0, 0, 0),
    output_format='png'
)
# third
fixed_ratio_expand('D:/path/to/your/mixed_img', 'D:/path/to/your/mixed_img/2JPEG', 1, 'white', 'JPEG')
