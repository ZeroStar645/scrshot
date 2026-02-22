import os
import uuid
import base64
import requests
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

def save_base64_to_file(api_url):
    try:
        response = requests.get(api_url, timeout=25)
        response.raise_for_status()
        data = response.json()
        base64_str = data.get("data")
        if not base64_str: return None
        if "," in base64_str: base64_str = base64_str.split(",")[-1]
        img_data = base64.b64decode(base64_str)
        file_name = f"temp_{uuid.uuid4().hex}.png"
        with open(file_name, "wb") as f:
            f.write(img_data)
        return os.path.abspath(file_name)
    except Exception as e:
        logger.error(f"Save image error: {e}")
        return None

@register("WebSiteScreenShot", "ZeroStaR", "网页截图", "1.1.1")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command_group("status")
    def status(self):
        pass
     
    @status.command("all")
    async def statusall(self, event: AstrMessageEvent):
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/api"
        async for res in self.handle_screenshot_send(event, url):
            yield res

    @status.command("equake")
    async def statusequake(self, event: AstrMessageEvent):
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/eq"
        async for res in self.handle_screenshot_send(event, url):
            yield res
                     
    async def statusequake(self, event: AstrMessageEvent):
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=https://he83e9571.nyat.app:50025/status.html"
        async for res in self.handle_screenshot_send(event, url):
            yield res


    async def handle_screenshot_send(self, event: AstrMessageEvent, url: str):
        file_path = save_base64_to_file(url)
        if file_path and os.path.exists(file_path):
            # 先 yield 结果给框架
            yield event.image_result(file_path)
            # 这里的删除逻辑可能需要稍微延迟，或者确认框架发送完。
            # 简单处理：如果报错文件被占用，说明发送中，通常 OS 会处理。
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Delete file failed: {e}")
        else:
            yield event.plain_result("❌ 截图失败")