const TodoModel = require('../models/todoModel');

class TodoController {
  static sendError(res, statusCode, message, details) {
    const payload = { error: message };

    if (details !== undefined) {
      payload.details = details;
    }

    return res.status(statusCode).json(payload);
  }

  // GET /api/todos
  static getTodos(req, res) {
    const { q, completed } = req.query;
    const todos = TodoModel.getAll({ q, completed });
    res.json(todos);
  }

  // GET /api/todos/stats
  static getTodoStats(req, res) {
    res.json(TodoModel.getStats());
  }

  // GET /api/todos/:id
  static getTodoById(req, res) {
    const todo = TodoModel.getById(req.params.id);
    if (!todo) {
      return this.sendError(res, 404, 'Todo not found');
    }
    res.json(todo);
  }

  // POST /api/todos
  static createTodo(req, res) {
    const { title, completed } = req.body;

    const newTodo = TodoModel.create({ title, completed });
    if (!newTodo) {
      return this.sendError(res, 400, 'Title is required', {
        field: 'title',
        received: title
      });
    }

    res.status(201).json(newTodo);
  }

  // PUT /api/todos/:id
  static updateTodo(req, res) {
    const { title, completed } = req.body;
    const updatedTodo = TodoModel.update(req.params.id, { title, completed });

    if (!updatedTodo) {
      if (title !== undefined && TodoModel.normalizeTitle(title) === null) {
        return this.sendError(res, 400, 'Title cannot be empty', {
          field: 'title',
          received: title
        });
      }

      return this.sendError(res, 404, 'Todo not found');
    }

    res.json(updatedTodo);
  }

  // POST /api/todos/:id/toggle
  static toggleTodo(req, res) {
    const toggledTodo = TodoModel.toggle(req.params.id);

    if (!toggledTodo) {
      return this.sendError(res, 404, 'Todo not found');
    }

    res.json(toggledTodo);
  }

  // DELETE /api/todos/:id
  static deleteTodo(req, res) {
    const deletedTodo = TodoModel.delete(req.params.id);
    if (!deletedTodo) {
      return this.sendError(res, 404, 'Todo not found');
    }

    res.json({ message: 'Todo deleted successfully', deletedTodo });
  }

  // DELETE /api/todos/completed
  static clearCompletedTodos(req, res) {
    const removedTodos = TodoModel.clearCompleted();

    res.json({
      message: 'Completed todos cleared successfully',
      removedCount: removedTodos.length,
      removedTodos
    });
  }
}

module.exports = TodoController;
