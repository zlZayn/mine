from PIL import Image
import os

def crop(width_step_pixel, input_image_path, crop_aspect_ratio=1/1, min_size_ratio=0.1, min_pixel_limit=100):
    """
    最终目的/动机
    Ultimate Purpose/Motivation
        按固定比例从图片中心进行裁剪，通过逐步缩小裁剪框并生成系列尺寸图像，便于筛选最适合的尺寸或去除边缘多余无用内容
        Crop images at a fixed aspect ratio from the center, generate a series of image sizes by gradually reducing the crop frame, facilitating selection of the most suitable size or removal of excess unwanted content from edges
        注意：该工具特别适用于图像主体位于中央区域的情况
        Notice: This tool is particularly suitable for images where the main subject is located in the central area
    
    功能说明
    Function Description
        - 从图像中心开始，按指定宽高比进行裁剪
        - Crop from the center of the image according to the specified aspect ratio
        - 每次迭代按指定步长缩小裁剪区域（保持宽高比不变）
        - Reduce the crop area by the specified step in each iteration (maintaining aspect ratio)
        - 持续生成裁剪图像，直至满足任一限制条件
        - Continuously generate cropped images until any limit condition is met
        
    输出文件保存位置
    Output File Save Location
        - 生成的图像保存在与原始照片相同目录下的新建文件夹中
        - Generated images are saved in a new folder within the same directory as the original photo
        
    输出文件命名规则
    Output File Naming Rules
        输出文件命名格式：原始文件名_crop{序号}_{宽度}_{高度}_{面积比例}.扩展名
        Output file naming format: original_filename_crop{index}_{width}_{height}_{area_ratio}.extension
        示例：image_crop1_1920_1080_1.0.jpg
        Example: image_crop1_1920_1080_1.0.jpg
        其中：
        Where:
        - 序号：裁剪序列索引（从1开始）
        - Index: Crop sequence index (starting from 1)
        - 宽度/高度：当前裁剪区域的像素尺寸
        - Width/Height: Pixel dimensions of the current crop area
        - 面积比例：当前裁剪区域面积与初始裁剪区域面积的比值
        - Area ratio: Ratio of current crop area to initial crop area
        
    参数
    Parameters
        - width_step_pixel: 每次缩小的宽度步长（像素）/ Width reduction step per iteration (pixels)
        - input_image_path: 输入图片路径/ Input image path
        - crop_aspect_ratio: 裁剪宽高比（默认1:1）/ Crop aspect ratio (default 1:1)
        - min_size_ratio: 最小尺寸比例（默认0.2）/ Minimum size ratio (default 0.2)
        - min_pixel_limit: 最小像素限制（默认100）/ Minimum pixel limit (default 100)
        
    终止条件
    Termination Conditions
        - 裁剪宽度/高度小于最小允许值（由最小尺寸比例和最小像素限制共同确定）
        - Crop width/height is less than the minimum allowed value (determined jointly by minimum size ratio and minimum pixel limit)
        - 裁剪区域面积比例小于最小尺寸比例
        - Crop area ratio is less than the minimum size ratio
        上述任一条件满足时，程序停止生成新的裁剪图像
        The program stops generating new cropped images when any of the conditions are met
    """
    # 创建输出文件夹/Create output directory
    output_directory = f"{os.path.splitext(input_image_path)[0]}_output"
    os.makedirs(output_directory, exist_ok=True)
    
    with Image.open(input_image_path) as source_image:
        # 获取图片尺寸/Get image dimensions
        source_width_pixel, source_height_pixel = source_image.size
        
        # 计算初始裁剪框（从中心）/Calculate initial crop frame (from center)
        if source_width_pixel / source_height_pixel > crop_aspect_ratio:
            current_crop_height_pixel = source_height_pixel
            current_crop_width_pixel = int(source_height_pixel * crop_aspect_ratio)
        else:
            current_crop_width_pixel = source_width_pixel
            current_crop_height_pixel = int(source_width_pixel / crop_aspect_ratio)
        
        # 计算最小允许尺寸/Calculate minimum allowed dimensions
        min_allowed_crop_width_pixel = max(current_crop_width_pixel * min_size_ratio, min_pixel_limit)
        min_allowed_crop_height_pixel = max(current_crop_height_pixel * min_size_ratio, min_pixel_limit)
        
        # 获取文件名信息/Get file name information
        original_file_name, file_extension = os.path.splitext(os.path.basename(input_image_path))
        crop_sequence_index = 1
        
        # 保存初始尺寸作为基准/Save initial dimensions as reference
        initial_crop_width_pixel = current_crop_width_pixel
        initial_crop_height_pixel = current_crop_height_pixel
        
        while True:
            # 计算当前面积比例/Calculate current area ratio
            relative_area_ratio = round(
                (current_crop_width_pixel * current_crop_height_pixel) / 
                (initial_crop_width_pixel * initial_crop_height_pixel), 5)
            
            # 检查终止条件：当前尺寸不满足要求/Check termination condition: current dimensions not meeting requirements
            if (current_crop_width_pixel < min_allowed_crop_width_pixel or 
                current_crop_height_pixel < min_allowed_crop_height_pixel or
                relative_area_ratio < min_size_ratio):
                reasons_zh = []
                reasons_en = []
                if current_crop_width_pixel < min_allowed_crop_width_pixel or current_crop_height_pixel < min_allowed_crop_height_pixel:
                    reasons_zh.append(f"宽/高限制(宽={current_crop_width_pixel}, 高={current_crop_height_pixel}) < 最小允许值(宽={min_allowed_crop_width_pixel}, 高={min_allowed_crop_height_pixel})")
                    reasons_en.append(f"Width/height limit(width={current_crop_width_pixel}, height={current_crop_height_pixel}) < min allowed values(width={min_allowed_crop_width_pixel}, height={min_allowed_crop_height_pixel})")
                if relative_area_ratio < min_size_ratio:
                    reasons_zh.append(f"面积比例限制(当前比例={relative_area_ratio}) < 最小比例({min_size_ratio})")
                    reasons_en.append(f"Area ratio limit(current ratio={relative_area_ratio}) < min ratio({min_size_ratio})")
                
                if reasons_zh and reasons_en:
                    print(f"停止生成图像 {crop_sequence_index}，原因：{', '.join(reasons_zh)}")
                    print(f"Stop generating image {crop_sequence_index}, reasons: {', '.join(reasons_en)}")
                break
                
            # 裁剪并保存图片/Crop and save image
            crop_left_position_pixel = (source_width_pixel - current_crop_width_pixel) // 2
            crop_top_position_pixel = (source_height_pixel - current_crop_height_pixel) // 2
            source_image.crop(
                (crop_left_position_pixel, crop_top_position_pixel, 
                 crop_left_position_pixel + current_crop_width_pixel, 
                 crop_top_position_pixel + current_crop_height_pixel)
            ).save(
                f"{output_directory}/{original_file_name}_crop{crop_sequence_index}_"
                f"{current_crop_width_pixel}_{current_crop_height_pixel}_{relative_area_ratio}{file_extension.lower()}")
            
            # 计算下一步尺寸/Calculate next dimensions
            next_crop_width_pixel = current_crop_width_pixel - width_step_pixel
            next_crop_height_pixel = next_crop_width_pixel / crop_aspect_ratio
            next_crop_width_pixel, next_crop_height_pixel = round(next_crop_width_pixel), round(next_crop_height_pixel)
            
            # 计算下一步面积比例/Calculate next area ratio
            next_relative_area_ratio = round(
                (next_crop_width_pixel * next_crop_height_pixel) / 
                (initial_crop_width_pixel * initial_crop_height_pixel), 5)
            
            # 检查下一步是否会触发终止条件/Check if next step will trigger termination condition
            if (next_crop_width_pixel < min_allowed_crop_width_pixel or 
                next_crop_height_pixel < min_allowed_crop_height_pixel or
                next_relative_area_ratio < min_size_ratio):
                reasons_zh = []
                reasons_en = []
                if next_crop_width_pixel < min_allowed_crop_width_pixel or next_crop_height_pixel < min_allowed_crop_height_pixel:
                    reasons_zh.append(f"下一步的 min(宽, 高)({next_crop_width_pixel}, {next_crop_height_pixel}) < 最小允许值({min_pixel_limit})")
                    reasons_en.append(f"Next step min(width, height)({next_crop_width_pixel}, {next_crop_height_pixel}) < min allowed value({min_pixel_limit})")
                if next_relative_area_ratio < min_size_ratio:
                    reasons_zh.append(f"下一步面积比例({next_relative_area_ratio}) < 最小比例({min_size_ratio})")
                    reasons_en.append(f"Next step area ratio({next_relative_area_ratio}) < min ratio({min_size_ratio})")
                
                if reasons_zh and reasons_en:
                    print(f"停止生成图像 {crop_sequence_index+1}，原因：{', '.join(reasons_zh)}")
                    print(f"Stop generating image {crop_sequence_index+1}, reasons: {', '.join(reasons_en)}")
                break
                
            # 更新尺寸和序号/Update dimensions and index
            current_crop_width_pixel, current_crop_height_pixel = next_crop_width_pixel, next_crop_height_pixel
            crop_sequence_index += 1
    
    print(f"完成！已生成 {crop_sequence_index} 张图像，保存在 {output_directory} 文件夹中")
    print(f"Completed! Generated {crop_sequence_index} images saved in {output_directory} folder")


# 使用示例/Usage example
# first
crop(
    width_step_pixel=20,
    input_image_path='D:\\path\\to\\your\\JPG\\Aaaawesome_photo_center.jpg',
    crop_aspect_ratio=16/9,
    min_size_ratio=0.0025,
    min_pixel_limit=100
)
# second
crop(5, "C:/path/to/your/PNG/small_photo_center.png", 1, 0.01, 50)