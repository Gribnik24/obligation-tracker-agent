import json
from langchain_core.messages import HumanMessage

from src.agent import agent, memory


def process_message(msg):
    """Обрабатывает одно сообщение и выводит соответствующий этап ReAct-цикла."""
    msg_type = type(msg).__name__

    if msg_type == 'AIMessage':
        # THOUGHT
        # reasoning_content - внутренние рассуждения модели (если поддерживается)
        reasoning = msg.additional_kwargs.get('reasoning_content')
        if reasoning:
            print(f'[THOUGHT]: {reasoning}')

        # Если reasoning_content недоступен, но модель вернула текст перед вызовом
        # инструментов - это тоже её "мыслительный" шаг
        if msg.tool_calls and msg.content and msg.content.strip() and not reasoning:
            print(f'[THOUGHT]: {msg.content}')

        # ACTION
        if msg.tool_calls:
            for tc in msg.tool_calls:
                if isinstance(tc, dict):
                    tool_name = tc.get('name', 'unknown')
                    tool_args = tc.get('args', {})
                else:
                    tool_name = getattr(tc, 'name', 'unknown')
                    tool_args = getattr(tc, 'args', {})
                print(f'[ACTION]: {tool_name}({json.dumps(tool_args, ensure_ascii=False)})')

        # FINAL ANSWER
        elif msg.content:
            print(f'[FINAL ANSWER]: {msg.content}')

    # OBSERVATION
    elif msg_type == 'ToolMessage':
        print(f'[OBSERVATION]: {msg.content}')


def main():
    while True:
        # Обработка пользовательского запроса
        query = input("USER: ").strip()
        lw_query = query.lower()

        # Условие завершения диалога
        if '/exit' in lw_query:
            break

        # Условие обнуления памяти
        if '/reset' in lw_query:
            memory.delete_thread(thread_id='test_thread')
            continue

        # Передача запроса агенту со стримингом для логирования в реальном времени
        config = {"configurable": {"thread_id": 'test_thread'}}

        try:
            for event in agent.stream(
                {'messages': [HumanMessage(content=query)]},
                config=config,
                stream_mode="updates"
            ):
                for node_name, state_update in event.items():
                    if "messages" not in state_update:
                        continue
                    for msg in state_update["messages"]:
                        process_message(msg)
        except Exception as e:
            print(f'[ERROR]: Ошибка при выполнении агента: {e}')


if __name__ == '__main__':
    main()