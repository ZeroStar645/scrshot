from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests

def get_base64_image_str(api_url):
    """
    获取 API 返回的 Base64 并处理成 AstrBot 可识别的 Data URI 格式
    """
    try:
        # 增加超时控制，防止接口响应慢导致机器人卡死
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        # 假设 Napcat 插件返回的 JSON 结构中 Base64 字符串在 "data" 字段
        base64_str = data.get("data") 
        
        if not base64_str:
            logger.warning(f"接口响应中未找到图片数据: {api_url}")
            return None

        # 核心修正：如果字符串不带前缀，手动加上，防止框架识别错误
        if isinstance(base64_str, str) and not base64_str.startswith("data:"):
            # 注意：Napcat 截图通常是 png 格式
            base64_str = f"data:image/png;base64,{base64_str}"
            
        return base64_str
    except Exception as e:
        logger.error(f"请求 Web 截图接口失败: {e}")
        return None

@register("WebSiteScreenShot", "ZeroStaR", "调取 Napcat 插件进行网页截图", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command_group("status")
    def status(self):
        """状态查询指令组"""
        pass
     
    @status.command("all")
    async def statusall(self, event: AstrMessageEvent):
        """查询所有服务状态"""
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/api"
        b64_data = get_base64_image_str(url)
        
        if b64_data:
            # 这里的 b64_data 是带前缀的字符串，AstrBot 能完美处理
            yield event.image_result(b64_data)
        else:
            yield event.plain_result("❌ 无法获取全量状态截图，请检查后端服务。")

    @status.command("equake")
    async def statusequake(self, event: AstrMessageEvent):
        """查询地震监控状态"""
        url = "http://napcat:6099/plugin/napcat-plugin-puppeteer/api/screenshot?url=http://uptime-kuma:3001/status/eq"
        b64_data = get_base64_image_str(url)
        
        if b64_data:
            yield event.image_result(b64_data)
        else:
            yield event.plain_result("❌ 无法获取地震监控截图。")

    async def terminate(self):
        """插件卸载时调用"""
        pass