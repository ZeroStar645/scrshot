import os
import uuid
import base64
import httpx
import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

async def async_save_base64_to_file(api_url):
    """异步请求截图接口并保存到本地"""
    try:
        async with httpx.AsyncClient() as client:
            # 增加超时时间到 30秒，因为截图服务通常较慢
            response = await client.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            base64_str = data.get("data")
            if not base64_str:
                return None
            
            # 去除 base64 前缀（如有）
            if "," in base64_str:
                base64_str = base64_str.split(",")[-1]
                
            img_data = base64.b64decode(base64_str)
            file_name = f"temp_{uuid.uuid4().hex}.png"
            
            # 写入本地文件
            with open(file_name, "wb") as f:
                f.write(img_data)
                
            return os.path.abspath(file_name)
    except Exception as e:
        logger.error(f"Async screenshot save error: {e}")
        return None

@register("WebSiteScreenShot", "ZeroStaR", "网页截图并发版", "1.2.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command_group("status")
    def status(self):
        pass

    @status.command("all")
    async def statusall(self, event: AstrMessageEvent):
        yield event.plain_result("处理图片中，请稍后..")
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/api"
        # 单张图片直接调用包装好的发送逻辑
        async for res in self.handle_multi_screenshots(event, [url]):
            yield res

    @status.command("equake")
    async def statusequake(self, event: AstrMessageEvent):
        yield event.plain_result("处理图片中，请稍后..")
        # 定义需要并发截取的 URL 列表
        urls = [
            "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/eq"
        ]
        
        # 调用并发处理逻辑
        async for res in self.handle_multi_screenshots(event, urls):
            yield res

    async def handle_multi_screenshots(self, event: AstrMessageEvent, urls: list):
        """核心并发处理逻辑"""
        # 并行发起所有网络请求
        tasks = [async_save_base64_to_file(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_any = False
        for path in results:
            if isinstance(path, str) and os.path.exists(path):
                # 发送图片
                yield event.image_result(path)
                success_any = True
                
                # 稍微延迟后删除，防止框架还没读取完文件就被删掉
                await asyncio.sleep(2) 
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    logger.error(f"Delete file failed: {e}")
        
        if not success_any:
            yield event.plain_result("❌ 截图任务全部失败，请检查网络或后端接口。")
