# mcp_client.py
import json

class MCPClient:
    def process(self, natural_text: str):
        """
        자연어 → JSON 명령으로 변환
        실제 구현에서는 MCP 서버로 HTTP/WebSocket 요청
        """

        # Mock 변환 로직
        if "모두 삭제" in natural_text:
            return {"action": "clear_text"}

        if "대문자" in natural_text:
            return {"action": "to_upper"}

        if "소문자" in natural_text:
            return {"action": "to_lower"}

        return {"action": "insert_text", "content": natural_text}