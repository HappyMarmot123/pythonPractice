import json
import os

FILE_NAME = 'todo_list.json'

# 1. 파일에서 목록 불러오기 (Read)
def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            # 파일이 비어있으면 빈 리스트 반환
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# 2. 목록 파일에 저장하기 (Save)
def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)
    print("✅ 할 일 목록이 저장되었습니다.")

# 3. 할 일 추가 (Create)
def add_task(tasks):
    task_content = input("새로운 할 일 내용을 입력하세요: ")
    if task_content:
        tasks.append({"task": task_content, "done": False})
        print(f"➕ '{task_content}'가 추가되었습니다.")
    else:
        print("내용이 없어 추가되지 않았습니다.")

# 4. 할 일 목록 출력 (Read)
def list_tasks(tasks):
    if not tasks:
        print("\n📝 할 일이 없습니다. 새로운 할 일을 추가하세요.\n")
        return

    print("\n--- To-Do List ---")
    for i, task_item in enumerate(tasks):
        status = "✅" if task_item['done'] else "◻️"
        print(f"{i + 1}. [{status}] {task_item['task']}")
    print("------------------\n")

# 5. 할 일 완료/미완료 상태 변경 (Update)
def toggle_task(tasks):
    list_tasks(tasks)
    if not tasks:
        return
        
    try:
        task_num = int(input("상태를 변경할 할 일 번호를 입력하세요: "))
        index = task_num - 1
        
        if 0 <= index < len(tasks):
            # 상태 반전 (True -> False, False -> True)
            tasks[index]['done'] = not tasks[index]['done']
            status = "완료" if tasks[index]['done'] else "미완료"
            print(f"🔄 {task_num}번 할 일의 상태가 '{status}'로 변경되었습니다.")
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 유효한 숫자를 입력하세요.")

# 6. 할 일 삭제 (Delete)
def delete_task(tasks):
    list_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("삭제할 할 일 번호를 입력하세요: "))
        index = task_num - 1

        if 0 <= index < len(tasks):
            deleted_task = tasks.pop(index)
            print(f"🗑️ '{deleted_task['task']}'가 삭제되었습니다.")
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 유효한 숫자를 입력하세요.")

# 메인 루프
def main():
    tasks = load_tasks()
    
    while True:
        print("\n=== To-Do CLI ===")
        print("1. 할 일 추가")
        print("2. 목록 보기")
        print("3. 상태 변경")
        print("4. 할 일 삭제")
        print("5. 저장 및 종료")
        
        choice = input("선택: ")
        
        if choice == '1':
            add_task(tasks)
        elif choice == '2':
            list_tasks(tasks)
        elif choice == '3':
            toggle_task(tasks)
        elif choice == '4':
            delete_task(tasks)
        elif choice == '5':
            save_tasks(tasks)
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("⛔ 올바른 메뉴 번호를 선택하세요 (1-5).")

if __name__ == "__main__":
    main()