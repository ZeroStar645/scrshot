import os
import uuid
import base64
import requests
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

def save_base64_to_file(api_url):
    """
    请求 API，解码 Base64 并保存为临时文件
    返回文件路径，如果失败返回 None
    """
    try:
        response = requests.get(api_url, timeout=20) # 截图可能较慢，给予充足时间
        response.raise_for_status()
        
        data = response.json()
        base64_str = data.get("data")
        
        if not base64_str:
            return None

        # 1. 清洗数据：去掉可能存在的 Data URI 前缀
        if "," in base64_str:
            base64_str = base64_str.split(",")[-1]

        # 2. 解码
        img_data = base64.b64decode(base64_str)

        # 3. 生成临时文件名（放在插件目录下或系统临时目录）
        # 使用 uuid 避免多人在同一秒截图时覆盖文件
        file_name = f"temp_screenshot_{uuid.uuid4().hex}.png"
        
        with open(file_name, "wb") as f:
            f.write(img_data)
            
        # 返回绝对路径确保 AstrBot 能找到
        return os.path.abspath(file_name)
        
    except Exception as e:
        logger.error(f"转换图片失败: {e}")
        return None

@register("WebSiteScreenShot", "ZeroStaR", "通过本地中转发送网页截图", "1.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command_group("status")
    def status(self):
        pass
     
    @status.command("all")
    async def statusall(self, event: AstrMessageEvent):
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/api"
        await self.handle_screenshot_send(event, url)

    @status.command("equake")
    async def statusequake(self, event: AstrMessageEvent):
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/eq"
        await self.handle_screenshot_send(event, url)

    async def handle_screenshot_send(self, event: AstrMessageEvent, url: str):
        """通用处理逻辑：下载 -> 发送 -> 删除"""
        file_path = save_base64_to_file(url)
        
        if file_path and os.path.exists(file_path):
            try:
                # 发送图片（传入本地绝对路径）
                yield event.image_result(file_path)
            finally:
                # 无论发送成功与否，都要删除临时文件防止占满磁盘
                try:
                    os.remove(file_path)
                    logger.info(f"临时文件已清理: {file_path}")
                except Exception as e:
                    logger.error(f"清理临时文件失败: {e}")
        else:
            yield event.plain_result("❌ 截图获取失败，请检查后端 API 或网络。")

    async def terminate(self):
        pass