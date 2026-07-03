let todos = [
  { id: 1, title: 'Learn Node.js & Express', completed: false },
  { id: 2, title: 'Build a mock backend', completed: true },
  { id: 3, title: 'Test the APIs', completed: false }
];

class TodoModel {
  static normalizeTitle(title) {
    if (title === undefined || title === null) {
      return null;
    }

    const normalized = String(title).trim().replace(/\s+/g, ' ');
    return normalized.length > 0 ? normalized : null;
  }

  static parseCompleted(value, fallback = false) {
    if (value === undefined || value === null || value === '') {
      return fallback;
    }

    if (typeof value === 'boolean') {
      return value;
    }

    if (typeof value === 'number') {
      return value !== 0;
    }

    if (typeof value === 'string') {
      const normalized = value.trim().toLowerCase();

      if (['true', '1', 'yes', 'y', 'on'].includes(normalized)) {
        return true;
      }

      if (['false', '0', 'no', 'n', 'off'].includes(normalized)) {
        return false;
      }
    }

    return Boolean(value);
  }

  static clone(todo) {
    return todo ? { ...todo } : null;
  }

  static findIndexById(id) {
    const parsedId = parseInt(id, 10);
    return Number.isNaN(parsedId)
      ? -1
      : todos.findIndex(todo => todo.id === parsedId);
  }

  static getAll({ q, completed } = {}) {
    let result = todos.map(todo => this.clone(todo));

    if (q) {
      const keyword = q.toLowerCase();
      result = result.filter(t => t.title.toLowerCase().includes(keyword));
    }

    if (completed !== undefined) {
      const isCompleted = this.parseCompleted(completed);
      result = result.filter(t => t.completed === isCompleted);
    }

    return result;
  }

  static getById(id) {
    const todo = todos.find(t => t.id === parseInt(id, 10));
    return this.clone(todo);
  }

  static create({ title, completed }) {
    const normalizedTitle = this.normalizeTitle(title);

    if (!normalizedTitle) {
      return null;
    }

    const newTodo = {
      id: todos.length > 0 ? Math.max(...todos.map(t => t.id)) + 1 : 1,
      title: normalizedTitle,
      completed: this.parseCompleted(completed, false)
    };

    todos.push(newTodo);
    return this.clone(newTodo);
  }

  static update(id, { title, completed }) {
    const todoIndex = this.findIndexById(id);
    if (todoIndex === -1) return null;

    const currentTodo = todos[todoIndex];

    if (title !== undefined) {
      const normalizedTitle = this.normalizeTitle(title);
      if (!normalizedTitle) {
        return null;
      }
      currentTodo.title = normalizedTitle;
    }

    if (completed !== undefined) {
      currentTodo.completed = this.parseCompleted(completed, currentTodo.completed);
    }

    return this.clone(currentTodo);
  }

  static delete(id) {
    const index = this.findIndexById(id);
    if (index === -1) return null;

    const deletedTodo = todos.splice(index, 1)[0];
    return this.clone(deletedTodo);
  }

  static toggle(id) {
    const todoIndex = this.findIndexById(id);
    if (todoIndex === -1) return null;

    todos[todoIndex].completed = !todos[todoIndex].completed;
    return this.clone(todos[todoIndex]);
  }

  static clearCompleted() {
    const remainingTodos = [];
    const removedTodos = [];

    for (const todo of todos) {
      if (todo.completed) {
        removedTodos.push(this.clone(todo));
      } else {
        remainingTodos.push(todo);
      }
    }

    todos = remainingTodos;

    return removedTodos;
  }

  static getStats() {
    const total = todos.length;
    const completed = todos.filter(todo => todo.completed).length;
    const active = total - completed;
    const completionRate = total === 0 ? 0 : Math.round((completed / total) * 100);

    const longestTitle = todos.reduce((currentLongest, todo) => {
      if (!currentLongest || todo.title.length > currentLongest.title.length) {
        return this.clone(todo);
      }

      return currentLongest;
    }, null);

    return {
      total,
      completed,
      active,
      completionRate,
      longestTitle
    };
  }
}

module.exports = TodoModel;
