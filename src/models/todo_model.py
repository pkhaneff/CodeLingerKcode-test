from typing import List, Dict, Any, Optional

todos = [
    {"id": 1, "title": "Learn Node.js & Express", "completed": False},
    {"id": 2, "title": "Build a mock backend", "completed": True},
    {"id": 3, "title": "Test the APIs", "completed": False}
]

class TodoModel:
    @staticmethod
    def get_all(q: Optional[str] = None, completed: Optional[str] = None) -> List[Dict[str, Any]]:
        result = todos
        
        if q:
            keyword = q.lower()
            result = [t for t in result if keyword in t["title"].lower()]
            
        if completed is not None:
            is_completed = completed.lower() == "true"
            result = [t for t in result if t["completed"] == is_completed]
            
        return result

    @staticmethod
    def get_by_id(todo_id: int) -> Optional[Dict[str, Any]]:
        for t in todos:
            if t["id"] == todo_id:
                return t
        return None

    @staticmethod
    def create(title: str, completed: bool = False) -> Dict[str, Any]:
        new_id = max([t["id"] for t in todos]) + 1 if todos else 1
        new_todo = {
            "id": new_id,
            "title": title,
            "completed": completed
        }
        todos.append(new_todo)
        return new_todo

    @classmethod
    def update(cls, todo_id: int, title: Optional[str] = None, completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        todo = cls.get_by_id(todo_id)
        if not todo:
            return None
            
        if title is not None:
            todo["title"] = title
        if completed is not None:
            todo["completed"] = completed
            
        return todo

    @staticmethod
    def delete(todo_id: int) -> Optional[Dict[str, Any]]:
        for i, t in enumerate(todos):
            if t["id"] == todo_id:
                return todos.pop(i)
        return None
