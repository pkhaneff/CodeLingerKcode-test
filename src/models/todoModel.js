let todos = [
  { id: 1, title: 'Learn Node.js & Express', completed: false },
  { id: 2, title: 'Build a mock backend', completed: true },
  { id: 3, title: 'Test the APIs', completed: false }
];

class TodoModel {
  static getAll({ q, completed } = {}) {
    let result = todos;

    if (q) {
      const keyword = q.toLowerCase();
      result = result.filter(t => t.title.toLowerCase().includes(keyword));
    }

    if (completed !== undefined) {
      const isCompleted = completed === 'true';
      result = result.filter(t => t.completed === isCompleted);
    }

    return result;
  }

  static getById(id) {
    return todos.find(t => t.id === parseInt(id));
  }

  static create({ title, completed }) {
    const newTodo = {
      id: todos.length > 0 ? Math.max(...todos.map(t => t.id)) + 1 : 1,
      title,
      completed: completed || false
    };
    todos.push(newTodo);
    return newTodo;
  }

  static update(id, { title, completed }) {
    const todo = this.getById(id);
    if (!todo) return null;

    if (title !== undefined) todo.title = title;
    if (completed !== undefined) todo.completed = completed;

    return todo;
  }

  static delete(id) {
    const index = todos.findIndex(t => t.id === parseInt(id));
    if (index === -1) return null;

    const deletedTodo = todos.splice(index, 1)[0];
    return deletedTodo;
  }
}

module.exports = TodoModel;
