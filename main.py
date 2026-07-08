import json
from langchain_core.messages import HumanMessage

from src.agent import agent, memory


def main():
    while True:
        # Обработка пользовательского запроса
        query = input("USER: ").strip()
        lw_query = query.lower()
        
        # Условие завершения диалога
        if lw_query == '/exit':
            break
        
        # Условие обнуления памяти
        if lw_query == '/reset':
            memory.delete_thread(thread_id='test_thread')
            continue
        
        # Передача обычного запроса
        config = {"configurable": {"thread_id": 'test_thread'}}
        response = agent.invoke({'messages': [HumanMessage(content=query)]},
                                 config=config)
        
        # Формируем просмотр сообщений с момента последнего пользовательского запроса
        last_human_idx = -1
        all_messages = response['messages']
        for i, msg in enumerate(all_messages):
            if type(msg).__name__ == 'HumanMessage':
                last_human_idx = i
        current_messages = all_messages[last_human_idx:]
        
        # Обрабатываем диалог и логируем TAO-цикл в консоль
        for msg in current_messages:
            msg_type = type(msg).__name__
            if msg_type == 'AIMessage':
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        reasoning = msg.additional_kwargs.get('reasoning_content')
                        if reasoning:
                            print(f'[THOUGHT]: {reasoning}')
                        
                        if isinstance(tc, dict):
                            tool_name = tc.get('name', 'unknown')
                            tool_args = tc.get('args', {})
                        else:
                            tool_name = getattr(tc, 'name', 'unknown')
                            tool_args = getattr(tc, 'args', {})
                            
                        print(f'[ACTION]: {tool_name}({json.dumps(tool_args, ensure_ascii=False)})')
                
                # Финальный ответ
                elif msg.content:
                    if msg != response['messages'][0]:
                        print(f'[FINAL ANSWER]: {msg.content}')
                        
            elif msg_type == 'ToolMessage':
                print(f'[OBSERVATION]: {msg.content}')

if __name__ == '__main__':
    main()