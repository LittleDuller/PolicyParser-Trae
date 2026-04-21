import json
import httpx


def interpret_api():
    """测试 interpret 接口的 SSE 流式输出"""
    url = "http://127.0.0.1:8000/api/v1/policy/interpret"

    # 构造请求体，与 InterpretRequest 结构保持一致
    payload = {
        "trace_id": "test_trace_123",
        "conversation_id": "test_conv_123",
        "turn_id": "test_turn_123",
        "policy_content": "关于进一步推进企业研发费用加计扣除政策落实的通知。本项目主要针对高新技术企业。",
        "policy_id": None,
    }

    print(f"开始请求: {url}")
    print("-" * 50)

    count = 0
    try:
        # 使用 httpx 的 stream 功能来接收 SSE 数据流
        with httpx.Client() as client:
            with client.stream("POST", url, json=payload, timeout=60.0) as response:
                # 如果状态码不是 200，说明请求出错，直接打印错误
                if response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}")
                    print(response.read().decode("utf-8"))
                    return

                # 遍历流式返回的每一行
                for line in response.iter_lines():
                    # print(line)
                    if line.startswith("data: "):
                        data_str = line[6:].strip()  # 截断 "data: " 前缀

                        # 检查流结束标识
                        if data_str == "[DONE]":
                            print("\n\n流接收完毕 [DONE]\n")
                            break

                        try:
                            # 解析 JSON 获取 content
                            data_json = json.loads(data_str)
                            if "content" in data_json:
                                content = data_json["content"]
                                print(content, end="", flush=True)
                                count += 1
                        except json.JSONDecodeError:
                            print(f"\n[解析 JSON 失败]: {data_str}")

    except httpx.ConnectError:
        print(
            "连接失败，请确认你的 FastAPI 服务是否已经在运行 (比如默认的 http://127.0.0.1:8000)"
        )

    print("-" * 50)
    print(f"测试结束，共接收到 {count} 个 content 块。")


if __name__ == "__main__":
    interpret_api()
