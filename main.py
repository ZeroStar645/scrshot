from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import base64
import requests

def base64_image(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        base64_str = data.get("data") 
        if not base64_str:
            logger.warning("未在响应中找到 Base64 数据")
            return
        img_data = base64.b64decode(base64_str)
        return img_data
    except Exception as e:
        logger.error(f"发生错误: {e}")

@register("WebSiteScreenShot", "ZeroStaR", "调取Napcat插件的渲染插件进行网页截图", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command_group("status")
    def status(self):
        pass
     
    @status.command("all")
    async def statusall(self, event: AstrMessageEvent):
        yield event.image_result(base64_image("http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?=http://uptime-kuma:3001/status/api")) 

    @status.command("equake")
    async def statusequake(self, event: AstrMessageEvent):
        yield event.image_result(base64_image("http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?=http://uptime-kuma:3001/status/eq")) 
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
