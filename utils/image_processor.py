import os
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
from typing import Dict, List, Any, Tuple
import io
import base64

def resize_image(image_path: str, target_size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
    """
    调整图片大小
    """
    try:
        with Image.open(image_path) as img:
            if maintain_aspect:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            return img.copy()
    except Exception as e:
        print(f"调整图片大小失败: {e}")
        return None

def add_border(image: Image.Image, border_width: int = 2, border_color: str = "#CCCCCC") -> Image.Image:
    """
    为图片添加边框
    """
    try:
        # 创建带边框的新图片
        new_width = image.width + 2 * border_width
        new_height = image.height + 2 * border_width
        
        bordered_img = Image.new('RGB', (new_width, new_height), border_color)
        bordered_img.paste(image, (border_width, border_width))
        
        return bordered_img
    except Exception as e:
        print(f"添加边框失败: {e}")
        return image

def add_rounded_corners(image: Image.Image, radius: int = 10) -> Image.Image:
    """
    为图片添加圆角
    """
    try:
        # 创建圆角蒙版
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + image.size, radius, fill=255)
        
        # 应用蒙版
        rounded_img = Image.new('RGBA', image.size, (0, 0, 0, 0))
        rounded_img.paste(image, (0, 0))
        rounded_img.putalpha(mask)
        
        return rounded_img
    except Exception as e:
        print(f"添加圆角失败: {e}")
        return image

def add_shadow(image: Image.Image, offset: Tuple[int, int] = (5, 5), blur_radius: int = 5, shadow_color: str = "#00000040") -> Image.Image:
    """
    为图片添加阴影效果
    """
    try:
        # 创建阴影层
        shadow_width = image.width + abs(offset[0]) + blur_radius * 2
        shadow_height = image.height + abs(offset[1]) + blur_radius * 2
        
        shadow_img = Image.new('RGBA', (shadow_width, shadow_height), (0, 0, 0, 0))
        
        # 绘制阴影
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_x = blur_radius + max(0, offset[0])
        shadow_y = blur_radius + max(0, offset[1])
        
        # 简化阴影：绘制一个半透明矩形
        shadow_draw.rectangle(
            [shadow_x, shadow_y, shadow_x + image.width, shadow_y + image.height],
            fill=shadow_color
        )
        
        # 应用模糊
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # 合成最终图片
        final_x = blur_radius + max(0, -offset[0])
        final_y = blur_radius + max(0, -offset[1])
        shadow_img.paste(image, (final_x, final_y), image if image.mode == 'RGBA' else None)
        
        return shadow_img
    except Exception as e:
        print(f"添加阴影失败: {e}")
        return image

def enhance_image(image: Image.Image, brightness: float = 1.0, contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
    """
    增强图片的亮度、对比度和饱和度
    """
    try:
        # 亮度调整
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        # 对比度调整
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # 饱和度调整
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        return image
    except Exception as e:
        print(f"图片增强失败: {e}")
        return image

def standardize_image_format(image: Image.Image, format: str = "PNG", quality: int = 95) -> Image.Image:
    """
    标准化图片格式
    """
    try:
        if image.mode != 'RGB' and format.upper() == 'JPEG':
            # JPEG不支持透明度，转换为RGB
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        
        return image
    except Exception as e:
        print(f"格式标准化失败: {e}")
        return image

def process_image_with_effects(image_path: str, effects: Dict[str, Any]) -> Image.Image:
    """
    根据效果配置处理图片
    """
    try:
        with Image.open(image_path) as img:
            processed_img = img.copy()
            
            # 调整大小
            if "resize" in effects:
                size = effects["resize"]
                processed_img = resize_image_from_pil(processed_img, size.get("size", (800, 600)), size.get("maintain_aspect", True))
            
            # 图片增强
            if "enhance" in effects:
                enhance = effects["enhance"]
                processed_img = enhance_image(
                    processed_img,
                    enhance.get("brightness", 1.0),
                    enhance.get("contrast", 1.0),
                    enhance.get("saturation", 1.0)
                )
            
            # 添加边框
            if "border" in effects:
                border = effects["border"]
                processed_img = add_border(
                    processed_img,
                    border.get("width", 2),
                    border.get("color", "#CCCCCC")
                )
            
            # 添加圆角
            if "rounded_corners" in effects:
                radius = effects["rounded_corners"].get("radius", 10)
                processed_img = add_rounded_corners(processed_img, radius)
            
            # 添加阴影
            if "shadow" in effects:
                shadow = effects["shadow"]
                processed_img = add_shadow(
                    processed_img,
                    shadow.get("offset", (5, 5)),
                    shadow.get("blur_radius", 5),
                    shadow.get("color", "#00000040")
                )
            
            return processed_img
    except Exception as e:
        print(f"图片处理失败: {e}")
        return None

def resize_image_from_pil(image: Image.Image, target_size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
    """
    从PIL图片对象调整大小
    """
    try:
        if maintain_aspect:
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
        else:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        print(f"调整图片大小失败: {e}")
        return image

def save_image(image: Image.Image, output_path: str, format: str = "PNG", quality: int = 95) -> bool:
    """
    保存图片到文件
    """
    try:
        image = standardize_image_format(image, format, quality)
        
        if format.upper() == 'JPEG':
            image.save(output_path, format=format, quality=quality, optimize=True)
        else:
            image.save(output_path, format=format, optimize=True)
        
        return True
    except Exception as e:
        print(f"保存图片失败: {e}")
        return False

def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    将PIL图片转换为base64字符串
    """
    try:
        buffer = io.BytesIO()
        image = standardize_image_format(image, format)
        image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_str}"
    except Exception as e:
        print(f"图片转base64失败: {e}")
        return ""

def batch_process_images(image_paths: List[str], effects: Dict[str, Any], output_dir: str = "processed") -> List[str]:
    """
    批量处理图片
    """
    processed_paths = []
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    for i, image_path in enumerate(image_paths):
        try:
            processed_img = process_image_with_effects(image_path, effects)
            if processed_img:
                output_filename = f"processed_{i+1}.png"
                output_path = os.path.join(output_dir, output_filename)
                
                if save_image(processed_img, output_path):
                    processed_paths.append(output_path)
                    print(f"已处理: {image_path} -> {output_path}")
                else:
                    print(f"保存失败: {image_path}")
            else:
                print(f"处理失败: {image_path}")
        except Exception as e:
            print(f"批量处理失败 {image_path}: {e}")
    
    return processed_paths

if __name__ == "__main__":
    # 测试图片处理功能
    test_effects = {
        "resize": {"size": (400, 300), "maintain_aspect": True},
        "enhance": {"brightness": 1.1, "contrast": 1.2},
        "border": {"width": 3, "color": "#2196F3"},
        "rounded_corners": {"radius": 15},
        "shadow": {"offset": (3, 3), "blur_radius": 8}
    }
    
    print("图片处理工具测试完成")
    print("支持的效果:", list(test_effects.keys()))