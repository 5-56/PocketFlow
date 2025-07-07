"""
Image Processor - 图像处理工具
支持图像调整、滤镜、格式转换等功能
"""
import io
import base64
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
import numpy as np

class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
        self.max_size = (4096, 4096)  # 最大尺寸限制
        
    def modify_image(self, image_data: bytes, operations: Dict[str, Any]) -> bytes:
        """修改图像"""
        try:
            # 加载图像
            image = Image.open(io.BytesIO(image_data))
            
            # 确保图像是RGB模式（除非是PNG需要保持透明度）
            if image.mode not in ['RGB', 'RGBA']:
                if image.mode == 'P' and 'transparency' in image.info:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
            
            # 应用各种操作
            for operation, params in operations.items():
                if operation == "resize":
                    image = self._resize_image(image, params)
                elif operation == "crop":
                    image = self._crop_image(image, params)
                elif operation == "rotate":
                    image = self._rotate_image(image, params)
                elif operation == "brightness":
                    image = self._adjust_brightness(image, params)
                elif operation == "contrast":
                    image = self._adjust_contrast(image, params)
                elif operation == "saturation":
                    image = self._adjust_saturation(image, params)
                elif operation == "sharpness":
                    image = self._adjust_sharpness(image, params)
                elif operation == "filter":
                    image = self._apply_filter(image, params)
                elif operation == "flip":
                    image = self._flip_image(image, params)
                elif operation == "color_balance":
                    image = self._adjust_color_balance(image, params)
            
            # 转换回字节
            output = io.BytesIO()
            
            # 确定输出格式
            output_format = operations.get("format", "JPEG")
            if output_format.upper() not in self.supported_formats:
                output_format = "JPEG"
            
            # 如果输出格式是JPEG但图像有透明度，转换为RGB
            if output_format.upper() == "JPEG" and image.mode == "RGBA":
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
                image = background
            
            # 保存图像
            save_kwargs = {}
            if output_format.upper() == "JPEG":
                save_kwargs["quality"] = operations.get("quality", 95)
                save_kwargs["optimize"] = True
            
            image.save(output, format=output_format, **save_kwargs)
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"图像处理失败: {str(e)}")
    
    def _resize_image(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整图像大小"""
        try:
            width = params.get("width")
            height = params.get("height")
            maintain_aspect = params.get("maintain_aspect", True)
            resample = getattr(Image.Resampling, params.get("resample", "LANCZOS"))
            
            if width and height:
                if maintain_aspect:
                    # 保持宽高比
                    image.thumbnail((width, height), resample)
                else:
                    # 强制调整到指定尺寸
                    image = image.resize((width, height), resample)
            elif width:
                # 只指定宽度，按比例调整高度
                ratio = width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((width, new_height), resample)
            elif height:
                # 只指定高度，按比例调整宽度
                ratio = height / image.height
                new_width = int(image.width * ratio)
                image = image.resize((new_width, height), resample)
            
            return image
            
        except Exception as e:
            raise Exception(f"图像尺寸调整失败: {str(e)}")
    
    def _crop_image(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """裁剪图像"""
        try:
            left = params.get("left", 0)
            top = params.get("top", 0)
            right = params.get("right", image.width)
            bottom = params.get("bottom", image.height)
            
            # 确保裁剪区域有效
            left = max(0, min(left, image.width))
            top = max(0, min(top, image.height))
            right = max(left, min(right, image.width))
            bottom = max(top, min(bottom, image.height))
            
            return image.crop((left, top, right, bottom))
            
        except Exception as e:
            raise Exception(f"图像裁剪失败: {str(e)}")
    
    def _rotate_image(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """旋转图像"""
        try:
            angle = params.get("angle", 0)
            expand = params.get("expand", True)
            fillcolor = params.get("fillcolor", (255, 255, 255))
            
            return image.rotate(angle, expand=expand, fillcolor=fillcolor)
            
        except Exception as e:
            raise Exception(f"图像旋转失败: {str(e)}")
    
    def _adjust_brightness(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整亮度"""
        try:
            factor = params.get("factor", 1.0)
            factor = max(0.1, min(3.0, factor))  # 限制在合理范围内
            
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise Exception(f"亮度调整失败: {str(e)}")
    
    def _adjust_contrast(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整对比度"""
        try:
            factor = params.get("factor", 1.0)
            factor = max(0.1, min(3.0, factor))  # 限制在合理范围内
            
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise Exception(f"对比度调整失败: {str(e)}")
    
    def _adjust_saturation(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整饱和度"""
        try:
            factor = params.get("factor", 1.0)
            factor = max(0.0, min(3.0, factor))  # 限制在合理范围内
            
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise Exception(f"饱和度调整失败: {str(e)}")
    
    def _adjust_sharpness(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整锐度"""
        try:
            factor = params.get("factor", 1.0)
            factor = max(0.0, min(3.0, factor))  # 限制在合理范围内
            
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise Exception(f"锐度调整失败: {str(e)}")
    
    def _apply_filter(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """应用滤镜"""
        try:
            filter_type = params.get("type", "none").lower()
            
            if filter_type == "blur":
                radius = params.get("radius", 1)
                return image.filter(ImageFilter.GaussianBlur(radius=radius))
            elif filter_type == "sharpen":
                return image.filter(ImageFilter.SHARPEN)
            elif filter_type == "edge_enhance":
                return image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == "edge_enhance_more":
                return image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            elif filter_type == "smooth":
                return image.filter(ImageFilter.SMOOTH)
            elif filter_type == "smooth_more":
                return image.filter(ImageFilter.SMOOTH_MORE)
            elif filter_type == "emboss":
                return image.filter(ImageFilter.EMBOSS)
            elif filter_type == "contour":
                return image.filter(ImageFilter.CONTOUR)
            elif filter_type == "detail":
                return image.filter(ImageFilter.DETAIL)
            else:
                return image
                
        except Exception as e:
            raise Exception(f"滤镜应用失败: {str(e)}")
    
    def _flip_image(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """翻转图像"""
        try:
            direction = params.get("direction", "horizontal").lower()
            
            if direction == "horizontal":
                return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif direction == "vertical":
                return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                return image
                
        except Exception as e:
            raise Exception(f"图像翻转失败: {str(e)}")
    
    def _adjust_color_balance(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """调整色彩平衡"""
        try:
            # 转换为numpy数组进行处理
            img_array = np.array(image)
            
            # 调整红、绿、蓝通道
            red_factor = params.get("red", 1.0)
            green_factor = params.get("green", 1.0)
            blue_factor = params.get("blue", 1.0)
            
            if len(img_array.shape) == 3:  # RGB图像
                img_array[:, :, 0] = np.clip(img_array[:, :, 0] * red_factor, 0, 255)
                img_array[:, :, 1] = np.clip(img_array[:, :, 1] * green_factor, 0, 255)
                img_array[:, :, 2] = np.clip(img_array[:, :, 2] * blue_factor, 0, 255)
            
            return Image.fromarray(img_array.astype(np.uint8))
            
        except Exception as e:
            raise Exception(f"色彩平衡调整失败: {str(e)}")
    
    def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """获取图像信息"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_data),
                "has_transparency": image.mode in ['RGBA', 'LA'] or 'transparency' in image.info
            }
            
        except Exception as e:
            return {"error": f"获取图像信息失败: {str(e)}"}
    
    def optimize_image(self, image_data: bytes, target_size_kb: Optional[int] = None) -> bytes:
        """优化图像文件大小"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # 如果没有指定目标大小，使用默认优化
            if target_size_kb is None:
                output = io.BytesIO()
                
                # 转换为RGB（如果需要）
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 使用较高质量保存
                image.save(output, format='JPEG', quality=85, optimize=True)
                return output.getvalue()
            
            # 二分查找最佳质量设置
            target_size = target_size_kb * 1024
            min_quality, max_quality = 20, 95
            best_data = None
            
            while min_quality <= max_quality:
                quality = (min_quality + max_quality) // 2
                output = io.BytesIO()
                
                temp_image = image.copy()
                if temp_image.mode == 'RGBA':
                    background = Image.new('RGB', temp_image.size, (255, 255, 255))
                    background.paste(temp_image, mask=temp_image.split()[-1])
                    temp_image = background
                elif temp_image.mode != 'RGB':
                    temp_image = temp_image.convert('RGB')
                
                temp_image.save(output, format='JPEG', quality=quality, optimize=True)
                data = output.getvalue()
                
                if len(data) <= target_size:
                    best_data = data
                    min_quality = quality + 1
                else:
                    max_quality = quality - 1
            
            return best_data if best_data else image_data
            
        except Exception as e:
            raise Exception(f"图像优化失败: {str(e)}")
    
    def create_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (200, 200)) -> bytes:
        """创建缩略图"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # 创建缩略图
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式
            output = io.BytesIO()
            
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            image.save(output, format='JPEG', quality=80, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"缩略图创建失败: {str(e)}")
    
    def convert_format(self, image_data: bytes, target_format: str) -> bytes:
        """转换图像格式"""
        try:
            image = Image.open(io.BytesIO(image_data))
            output = io.BytesIO()
            
            target_format = target_format.upper()
            if target_format not in self.supported_formats:
                raise ValueError(f"不支持的目标格式: {target_format}")
            
            # 格式转换处理
            if target_format == 'JPEG' and image.mode in ['RGBA', 'LA']:
                # JPEG不支持透明度，添加白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif target_format == 'PNG' and image.mode not in ['RGBA', 'RGB', 'L']:
                image = image.convert('RGBA')
            
            # 保存参数
            save_kwargs = {}
            if target_format == 'JPEG':
                save_kwargs['quality'] = 95
                save_kwargs['optimize'] = True
            elif target_format == 'PNG':
                save_kwargs['optimize'] = True
            
            image.save(output, format=target_format, **save_kwargs)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"格式转换失败: {str(e)}")
    
    def auto_enhance(self, image_data: bytes) -> bytes:
        """自动增强图像"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # 自动色彩平衡
            image = ImageOps.autocontrast(image)
            
            # 轻微锐化
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # 轻微对比度增强
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.05)
            
            # 保存结果
            output = io.BytesIO()
            
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            image.save(output, format='JPEG', quality=90, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"自动增强失败: {str(e)}")